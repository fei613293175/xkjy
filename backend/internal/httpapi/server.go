package httpapi

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"log/slog"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/fei613293175/xkjy/backend/internal/config"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
)

const release = "P00"

var requestIDPattern = regexp.MustCompile("^[A-Za-z0-9_-]{8,80}$")

type dependencyChecker interface {
	Ready(context.Context) map[string]string
	Close()
}
type dependencies struct {
	database *pgxpool.Pool
	redis    *redis.Client
	required bool
}

func newDependencies(ctx context.Context, cfg config.Config, logger *slog.Logger) dependencyChecker {
	deps := dependencies{required: cfg.RequireDependencies}
	if !cfg.RequireDependencies {
		return deps
	}
	if pool, err := pgxpool.New(ctx, cfg.DatabaseURL); err != nil {
		logger.Error("database_connection_initialization_failed", "error", err.Error())
	} else {
		deps.database = pool
	}
	if options, err := redis.ParseURL(cfg.RedisURL); err != nil {
		logger.Error("redis_connection_initialization_failed", "error", err.Error())
	} else {
		deps.redis = redis.NewClient(options)
	}
	return deps
}

func (d dependencies) Ready(ctx context.Context) map[string]string {
	if !d.required {
		return map[string]string{"postgres": "not_required", "redis": "not_required"}
	}
	state := map[string]string{}
	if d.database == nil {
		state["postgres"] = "unavailable"
	} else if err := d.database.Ping(ctx); err != nil {
		state["postgres"] = "unavailable"
	} else {
		state["postgres"] = "ready"
	}
	if d.redis == nil {
		state["redis"] = "unavailable"
	} else if err := d.redis.Ping(ctx).Err(); err != nil {
		state["redis"] = "unavailable"
	} else {
		state["redis"] = "ready"
	}
	return state
}

func (d dependencies) Close() {
	if d.database != nil {
		d.database.Close()
	}
	if d.redis != nil {
		_ = d.redis.Close()
	}
}

func New(ctx context.Context, cfg config.Config, logger *slog.Logger) (http.Handler, func()) {
	deps := newDependencies(ctx, cfg, logger)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(writer http.ResponseWriter, request *http.Request) {
		writeJSON(writer, http.StatusOK, map[string]any{"status": "ok", "release": release})
	})
	mux.HandleFunc("GET /readyz", func(writer http.ResponseWriter, request *http.Request) {
		dependencyStatus := deps.Ready(request.Context())
		ready := true
		for _, state := range dependencyStatus {
			ready = ready && (state == "ready" || state == "not_required")
		}
		status := http.StatusOK
		label := "ready"
		if !ready {
			status = http.StatusServiceUnavailable
			label = "not_ready"
		}
		writeJSON(writer, status, map[string]any{"status": label, "release": release, "dependencies": dependencyStatus})
	})
	mux.HandleFunc("GET /v1/baseline", func(writer http.ResponseWriter, request *http.Request) {
		writeJSON(writer, http.StatusOK, map[string]any{"release": release, "scope": []string{"repository", "docker", "postgresql", "redis", "android_shell", "admin_shell", "resource_registry", "visual_gate"}, "configuration": cfg.SafeFields()})
	})
	return withRequestLogging(logger, mux), deps.Close
}

func withRequestLogging(logger *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		requestID := request.Header.Get("X-Request-ID")
		if !requestIDPattern.MatchString(requestID) {
			requestID = newRequestID()
		}
		writer.Header().Set("X-Request-ID", requestID)
		start := time.Now()
		statusWriter := &responseWriter{ResponseWriter: writer, status: http.StatusOK}
		defer func() {
			if recovered := recover(); recovered != nil {
				logger.Error("panic_recovered", "request_id", requestID, "path", request.URL.Path)
				if !statusWriter.wroteHeader {
					writeJSON(statusWriter, http.StatusInternalServerError, map[string]string{"error": "internal_error", "request_id": requestID})
				}
			}
			logger.Info("http_request", "request_id", requestID, "method", request.Method, "path", request.URL.Path, "status", statusWriter.status, "duration_ms", time.Since(start).Milliseconds())
		}()
		next.ServeHTTP(statusWriter, request)
	})
}

type responseWriter struct {
	http.ResponseWriter
	status      int
	wroteHeader bool
}

func (w *responseWriter) WriteHeader(status int) {
	if !w.wroteHeader {
		w.status = status
		w.wroteHeader = true
		w.ResponseWriter.WriteHeader(status)
	}
}
func (w *responseWriter) Write(body []byte) (int, error) {
	if !w.wroteHeader {
		w.WriteHeader(http.StatusOK)
	}
	return w.ResponseWriter.Write(body)
}
func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}
func newRequestID() string {
	bytes := make([]byte, 12)
	if _, err := rand.Read(bytes); err != nil {
		return strings.ReplaceAll(time.Now().UTC().Format("20060102150405.000000000"), ".", "")
	}
	return hex.EncodeToString(bytes)
}
