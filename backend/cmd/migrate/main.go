package main

import (
	"context"
	"log/slog"
	"os"
	"time"

	"github.com/fei613293175/xkjy/backend/internal/config"
	"github.com/fei613293175/xkjy/backend/internal/migrate"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	cfg, err := config.Load()
	if err != nil {
		logger.Error("invalid_runtime_configuration", "error", err.Error())
		os.Exit(1)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	if err := migrate.Apply(ctx, cfg.DatabaseURL, cfg.MigrationDir); err != nil {
		logger.Error("migration_failed", "directory", cfg.MigrationDir, "error", err.Error())
		os.Exit(1)
	}
	logger.Info("migration_complete", "directory", cfg.MigrationDir)
}
