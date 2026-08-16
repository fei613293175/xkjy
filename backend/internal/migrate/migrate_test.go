package migrate

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadSortsAndChecksumsMigrations(t *testing.T) {
	directory := t.TempDir()
	if err := os.WriteFile(filepath.Join(directory, "0002_second.sql"), []byte("SELECT 2;"), 0o600); err != nil { t.Fatal(err) }
	if err := os.WriteFile(filepath.Join(directory, "0001_first.sql"), []byte("SELECT 1;"), 0o600); err != nil { t.Fatal(err) }
	files, err := load(directory)
	if err != nil { t.Fatal(err) }
	if len(files) != 2 || files[0].Version != 1 || files[1].Version != 2 { t.Fatalf("unexpected migration order: %#v", files) }
	if len(files[0].Checksum) != 64 { t.Fatalf("unexpected checksum: %q", files[0].Checksum) }
}
