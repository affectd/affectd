package main

import (
	"errors"
	"strings"
	"testing"
)

func TestRun(t *testing.T) {
	tests := []struct {
		name       string
		args       []string
		wantCode   int
		wantStdout string
		wantStderr string
	}{
		{name: "version", args: []string{"version"}, wantStdout: "affectd dev (unknown)\n"},
		{name: "help", args: []string{"help"}, wantStdout: usage},
		{name: "short help flag", args: []string{"-h"}, wantStdout: usage},
		{name: "long help flag", args: []string{"--help"}, wantStdout: usage},
		{name: "no command", args: nil, wantCode: 2, wantStderr: usage},
		{name: "unknown command", args: []string{"scna"}, wantCode: 2, wantStderr: usage},
		{name: "extra argument", args: []string{"version", "extra"}, wantCode: 2, wantStderr: usage},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var stdout, stderr strings.Builder
			if code := run(tt.args, &stdout, &stderr); code != tt.wantCode {
				t.Errorf("run(%q) exit code = %d, want %d", tt.args, code, tt.wantCode)
			}
			if got := stdout.String(); got != tt.wantStdout {
				t.Errorf("run(%q) stdout = %q, want %q", tt.args, got, tt.wantStdout)
			}
			if got := stderr.String(); got != tt.wantStderr {
				t.Errorf("run(%q) stderr = %q, want %q", tt.args, got, tt.wantStderr)
			}
		})
	}
}

// brokenWriter fails every write, like stdout redirected to a full disk.
type brokenWriter struct{}

func (brokenWriter) Write([]byte) (int, error) { return 0, errors.New("no space left on device") }

func TestRunWriteError(t *testing.T) {
	for _, args := range [][]string{{"version"}, {"help"}} {
		var stderr strings.Builder
		if code := run(args, brokenWriter{}, &stderr); code != 1 {
			t.Errorf("run(%q) with a failing stdout: exit code = %d, want 1", args, code)
		}
		if got, want := stderr.String(), "affectd: write output: no space left on device\n"; got != want {
			t.Errorf("run(%q) with a failing stdout: stderr = %q, want %q", args, got, want)
		}
	}
}
