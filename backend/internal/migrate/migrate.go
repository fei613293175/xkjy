package migrate

import (
	"context"
	"crypto/sha256"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var migrationName = regexp.MustCompile("^(\\d+)_[a-z0-9_]+\\.sql$")

type file struct {
	Version             int64
	Name, SQL, Checksum string
}

func Apply(ctx context.Context, databaseURL, directory string) error {
	migrations, err := load(directory)
	if err != nil {
		return err
	}
	poolConfig, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return fmt.Errorf("parse database URL: %w", err)
	}
	poolConfig.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol
	pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		return fmt.Errorf("connect database: %w", err)
	}
	defer pool.Close()
	if _, err := pool.Exec(ctx, "CREATE TABLE IF NOT EXISTS schema_migrations (version bigint PRIMARY KEY, name text NOT NULL, checksum char(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())"); err != nil {
		return fmt.Errorf("create migration ledger: %w", err)
	}
	for _, current := range migrations {
		var saved string
		err := pool.QueryRow(ctx, "SELECT checksum FROM schema_migrations WHERE version = $1", current.Version).Scan(&saved)
		if err == nil {
			if saved != current.Checksum {
				return fmt.Errorf("migration %s checksum changed after application", current.Name)
			}
			continue
		}
		if err != pgx.ErrNoRows {
			return fmt.Errorf("read migration ledger for %s: %w", current.Name, err)
		}
		tx, err := pool.Begin(ctx)
		if err != nil {
			return fmt.Errorf("begin migration %s: %w", current.Name, err)
		}
		if _, err = tx.Exec(ctx, current.SQL); err == nil {
			_, err = tx.Exec(ctx, "INSERT INTO schema_migrations (version, name, checksum) VALUES ($1, $2, $3)", current.Version, current.Name, current.Checksum)
		}
		if err != nil {
			_ = tx.Rollback(ctx)
			return fmt.Errorf("apply migration %s: %w", current.Name, err)
		}
		if err := tx.Commit(ctx); err != nil {
			return fmt.Errorf("commit migration %s: %w", current.Name, err)
		}
	}
	return nil
}

func load(directory string) ([]file, error) {
	entries, err := os.ReadDir(directory)
	if err != nil {
		return nil, fmt.Errorf("read migration directory %q: %w", directory, err)
	}
	files := make([]file, 0, len(entries))
	versions := map[int64]string{}
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}
		matches := migrationName.FindStringSubmatch(entry.Name())
		if matches == nil {
			return nil, fmt.Errorf("invalid migration file name %q", entry.Name())
		}
		version, err := strconv.ParseInt(matches[1], 10, 64)
		if err != nil || version < 1 {
			return nil, fmt.Errorf("invalid migration version %q", entry.Name())
		}
		if existing, found := versions[version]; found {
			return nil, fmt.Errorf("duplicate migration version %d in %s and %s", version, existing, entry.Name())
		}
		contents, err := os.ReadFile(filepath.Join(directory, entry.Name()))
		if err != nil {
			return nil, fmt.Errorf("read migration %q: %w", entry.Name(), err)
		}
		if strings.TrimSpace(string(contents)) == "" {
			return nil, fmt.Errorf("migration %q is empty", entry.Name())
		}
		sum := sha256.Sum256(contents)
		versions[version] = entry.Name()
		files = append(files, file{Version: version, Name: entry.Name(), SQL: string(contents), Checksum: fmt.Sprintf("%x", sum)})
	}
	if len(files) == 0 {
		return nil, fmt.Errorf("no migrations found in %q", directory)
	}
	sort.Slice(files, func(i, j int) bool { return files[i].Version < files[j].Version })
	return files, nil
}
