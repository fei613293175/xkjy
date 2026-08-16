package config

import "testing"

func TestSafeFieldsNeverExposeConnectionValues(t *testing.T) {
	cfg := Config{Environment: "test", DatabaseURL: "postgres://secret", RedisURL: "redis://secret", RequireDependencies: true}
	fields := cfg.SafeFields()
	for key, value := range fields {
		if rendered, ok := value.(string); ok && (rendered == cfg.DatabaseURL || rendered == cfg.RedisURL) { t.Fatalf("field %s exposed a connection value", key) }
	}
}
