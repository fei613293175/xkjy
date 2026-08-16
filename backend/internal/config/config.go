package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config contains runtime wiring only. Credentials are supplied from server-only storage.
type Config struct {
	Environment         string
	HTTPAddr            string
	DatabaseURL         string
	RedisURL            string
	MigrationDir        string
	RequireDependencies bool
}

func Load() (Config, error) {
	cfg := Config{
		Environment:         value("APP_ENV", "production"),
		HTTPAddr:            value("HTTP_ADDR", ":8080"),
		DatabaseURL:         strings.TrimSpace(os.Getenv("DATABASE_URL")),
		RedisURL:            strings.TrimSpace(os.Getenv("REDIS_URL")),
		MigrationDir:        value("MIGRATION_DIR", "migrations"),
		RequireDependencies: boolValue("REQUIRE_DEPENDENCIES", true),
	}
	if cfg.RequireDependencies && (cfg.DatabaseURL == "" || cfg.RedisURL == "") {
		return Config{}, fmt.Errorf("DATABASE_URL and REDIS_URL are required when dependencies are enabled")
	}
	return cfg, nil
}

func (c Config) SafeFields() map[string]any {
	return map[string]any{
		"environment":           c.Environment,
		"dependencies_required": c.RequireDependencies,
		"database_configured":   c.DatabaseURL != "",
		"redis_configured":      c.RedisURL != "",
	}
}

func value(key, fallback string) string {
	if current := strings.TrimSpace(os.Getenv(key)); current != "" {
		return current
	}
	return fallback
}

func boolValue(key string, fallback bool) bool {
	current := strings.TrimSpace(os.Getenv(key))
	if current == "" {
		return fallback
	}
	parsed, err := strconv.ParseBool(current)
	if err != nil {
		return fallback
	}
	return parsed
}
