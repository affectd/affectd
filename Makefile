# Quality gates. `make check` is the definition of done, and CI runs the same
# targets. Go tools are pinned in go.mod with `go get -tool` and run through
# `go tool`, so everyone uses the same reviewed versions. golangci-lint is a
# pinned release binary, as its maintainers recommend.

GO       ?= go
PKGS     ?= ./...
FUZZTIME ?= 30s
BENCH    ?= .
# Packages whose tests must catch deliberately injected bugs.
CRITICAL ?= internal/match internal/safeio internal/data

.PHONY: check fmt-check vet lint test vuln fuzz bench bench-compare cover mutation proto

check: fmt-check vet lint test vuln

fmt-check:
	@out=$$(gofmt -l $$(git ls-files '*.go')); \
	if [ -n "$$out" ]; then echo "Not gofmt-formatted:"; echo "$$out"; exit 1; fi

vet:
	$(GO) vet $(PKGS)

lint:
	golangci-lint run

test:
	$(GO) test -race -shuffle=on -count=1 $(PKGS)

vuln:
	$(GO) tool govulncheck $(PKGS)

# Every fuzz target, FUZZTIME each.
fuzz:
	@for pkg in $$($(GO) list $(PKGS)); do \
	  for f in $$($(GO) test -list '^Fuzz' $$pkg | grep '^Fuzz'); do \
	    echo "fuzz $$pkg $$f"; \
	    $(GO) test -run '^$$' -fuzz "^$$f$$" -fuzztime $(FUZZTIME) $$pkg || exit 1; \
	  done; \
	done

# Ten runs per benchmark, so benchstat can tell real changes from noise.
bench:
	@mkdir -p bench
	$(GO) test -run '^$$' -bench '$(BENCH)' -benchmem -count 10 $(PKGS) | tee bench/new.txt

# Save a baseline first: on main, run `make bench && mv bench/new.txt bench/base.txt`.
bench-compare:
	$(GO) tool benchstat bench/base.txt bench/new.txt

cover:
	$(GO) test -coverprofile=cover.out $(PKGS)
	$(GO) tool cover -func=cover.out | tail -1

# Mutation testing on the critical packages: surviving mutants are bugs the
# tests would miss. Slow, so CI runs it weekly rather than on every change.
mutation:
	@for p in $(CRITICAL); do $(GO) tool gremlins unleash ./$$p || exit 1; done

proto:
	buf lint
	buf generate
