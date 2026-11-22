# Quality gates. `make check` is the definition of done, and CI runs the same
# targets. Go tools are pinned in go.mod with `go get -tool` and run through
# `go tool`, so everyone uses the same reviewed versions. golangci-lint is a
# pinned release binary, as its maintainers recommend.

# Recipes that pipe or loop set -o pipefail or -e themselves: macOS ships
# GNU Make 3.81, which ignores .SHELLFLAGS.
SHELL    := /bin/bash
GO       ?= go
PKGS     ?= ./...
FUZZTIME ?= 30s
BENCH    ?= .
# Packages whose tests must catch deliberately injected bugs.
CRITICAL ?= internal/match internal/safeio internal/data

.PHONY: check fmt-check vet lint lint-rules test vuln fuzz bench bench-compare cover mutation proto

check: fmt-check vet lint lint-rules test vuln

fmt-check:
	@out=$$(gofmt -l $$(git ls-files '*.go')); \
	if [ -n "$$out" ]; then echo "Not gofmt-formatted:"; echo "$$out"; exit 1; fi

vet:
	$(GO) vet $(PKGS)

# --config is explicit: golangci-lint would otherwise prefer a .golangci.yaml,
# .json or .toml added next to .golangci.yml.
lint:
	golangci-lint run --config .golangci.yml

# Each lint rule must reject a deliberate violation in testdata/lint/.
lint-rules:
	python3 scripts/check-lint-rules.py

test:
	$(GO) test -race -shuffle=on -count=1 $(PKGS)

vuln:
	$(GO) tool govulncheck $(PKGS)

# Every fuzz target, FUZZTIME each. The lists are captured first so that a
# package that doesn't compile fails here instead of fuzzing nothing.
fuzz:
	@set -e; pkgs=$$($(GO) list $(PKGS)); \
	for pkg in $$pkgs; do \
	  tests=$$($(GO) test -list '^Fuzz' $$pkg); \
	  for f in $$(grep '^Fuzz' <<< "$$tests" || true); do \
	    echo "fuzz $$pkg $$f"; \
	    $(GO) test -run '^$$' -fuzz "^$$f$$" -fuzztime $(FUZZTIME) $$pkg; \
	  done; \
	done

# Ten runs per benchmark, so benchstat can tell real changes from noise.
# pipefail: a failing benchmark must fail the target, not just tee's exit code.
# Results reach bench/new.txt only from a complete run, so bench-compare never
# reads a partial one.
bench:
	@mkdir -p bench
	set -o pipefail; $(GO) test -run '^$$' -bench '$(BENCH)' -benchmem -count 10 $(PKGS) | tee bench/new.txt.partial
	mv bench/new.txt.partial bench/new.txt

# Save a baseline first: on main, run `make bench && mv bench/new.txt bench/base.txt`.
bench-compare:
	$(GO) tool benchstat bench/base.txt bench/new.txt

cover:
	$(GO) test -coverprofile=cover.out $(PKGS)
	$(GO) tool cover -func=cover.out | tail -1

# Mutation testing on the critical packages: surviving mutants are bugs the
# tests would miss. Slow, so CI runs it weekly rather than on every change.
# A package that doesn't exist yet is skipped with a warning on the run summary.
mutation:
	@set -e; for p in $(CRITICAL); do \
	  if [ ! -d "$$p" ]; then echo "::warning::$$p doesn't exist yet, so it wasn't mutation-tested"; continue; fi; \
	  $(GO) tool gremlins unleash ./$$p; \
	done

proto:
	buf lint
	buf generate
