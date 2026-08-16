package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/fei613293175/xkjy/backend/internal/config"
	"github.com/fei613293175/xkjy/backend/internal/httpapi"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	cfg, err := config.Load()
	if err != nil {
		logger.Error("invalid_runtime_configuration", "error", err.Error())
		os.Exit(1)
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	handler, closeDependencies := httpapi.New(ctx, cfg, logger)
	defer closeDependencies()
	server := &http.Server{Addr: cfg.HTTPAddr, Handler: handler, ReadHeaderTimeout: 5 * time.Second, IdleTimeout: 60 * time.Second}
	go func() {
		logger.Info("api_started", "address", cfg.HTTPAddr, "environment", cfg.Environment)
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Error("api_stopped_unexpectedly", "error", err.Error())
			stop()
		}
	}()
	<-ctx.Done()
	shutdownContext, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(shutdownContext); err != nil {
		logger.Error("api_shutdown_failed", "error", err.Error())
	}
}
