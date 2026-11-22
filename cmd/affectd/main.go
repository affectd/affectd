// Command affectd detects supply-chain attacks on developer machines.
package main

import (
	"fmt"
	"io"
	"os"
)

// Release builds set these with -ldflags -X (see .goreleaser.yaml).
var (
	version = "dev"
	commit  = "unknown"
)

const usage = `Usage: affectd <command>

Commands:
  version  Print the version and the commit it was built from
  help     Print this help
`

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

// run executes the command in args and returns the process exit code: 0 on
// success, 1 if the output can't be written, and 2 for a usage error, which
// prints the usage to stderr.
func run(args []string, stdout, stderr io.Writer) int {
	command := ""
	if len(args) == 1 {
		command = args[0]
	}
	var err error
	switch command {
	case "version":
		_, err = fmt.Fprintf(stdout, "affectd %s (%s)\n", version, commit)
	case "help", "-h", "--help":
		_, err = io.WriteString(stdout, usage)
	default:
		_, _ = io.WriteString(stderr, usage) // stderr is the last place to report a failure
		return 2
	}
	if err != nil {
		_, _ = fmt.Fprintf(stderr, "affectd: write output: %v\n", err)
		return 1
	}
	return 0
}
