GO ?= go
GOOS := $(shell $(GO) env GOOS)
EXT := so
ifeq ($(GOOS),darwin)
EXT := dylib
endif
ifeq ($(GOOS),windows)
EXT := dll
endif

.PHONY: build test
build:
	mkdir -p dist
	CGO_ENABLED=1 $(GO) build -buildmode=c-shared -o dist/cursor.$(EXT) .

test:
	$(GO) test -race ./...
	$(GO) vet ./...
