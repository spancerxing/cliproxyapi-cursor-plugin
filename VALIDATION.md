# Native version 0.1.0 validation

Execution format compatibility: CPA normalizes Chat Completions to `openai`.
The executor accepts that canonical name and Chat Completions aliases. Host HTTP
fixtures cover streaming and non-streaming execution with both `openai` and
`chat-completions`; other protocol payloads remain rejected by the plugin.

The initial release includes the Cursor display name, the official Cursor app icon,
and a plugin resource page for API key login. The page calls a CPA-authenticated
management route; keys are validated through the CPA HTTP callback and saved via
`host.auth.save`. Synthetic tests cover successful persistence, invalid input,
upstream rejection, network/server errors, and persistence failures. The C ABI
smoke test also checks management registration and HTML resource rendering.
Real Cursor credentials and a deployed CPA management UI still require testing.

## Earlier validation history

Store publishing support added on 2026-10-21:

- Go race tests, `go vet`, and the updated native C ABI smoke test passed locally.
- Six publishing tests passed: release completeness, checksum tampering, ZIP path
  rejection, architecture mismatch, registry append/duplicate checks, and refusing
  to submit a store PR when release assets are missing.
- Workflow YAML, Bash syntax and Python syntax were checked locally.
- Linux AMD64/ARM64 and Windows AMD64 builds are configured in GitHub Actions.
  They have not yet run; their native libraries are not locally built or verified.
  No macOS release archive is configured.
- No GitHub Release or official store PR has been created by this change.
  Shell access to GitHub fails DNS resolution in the current environment.

Environment: macOS ARM64, Go 1.26.0. There are no third-party Go modules.

Passed:

- `go test -race ./...`: 932 test/subtest cases, including 864 model resolution
  cases compared with checked-in expectations from the MIT reference.
- Conversation parity: system/developer prompts, split tool calls, missing
  results, reasoning, inline images and tool-result content.
- Protobuf value parity, malformed argument rejection, compressed Connect
  frames, protocol error status mapping, and seeded binary parser fuzz cases.
- In-process CPA HTTP fixtures exercise real native RunSSE/BidiAppend,
  content-addressed transcript blob requests, tool call delivery, rebuilding
  history with a real client tool result, and final model output.
- HTTP response-head and silent-read cancellation, callback context propagation,
  status preservation, concurrent account isolation, API key exchange caching,
  PKCE browser login, expiry, quota windows and on-demand team pool behavior.
- An intermittent error-path cleanup race found during migration was fixed.
  Cancellation and error cleanup tests then passed 20 consecutive race runs.
- `go vet ./...`.
- `go build -buildmode=c-shared -o dist/cursor.dylib .`.
- The compiled native test binary passed with `PATH=/nonexistent` and
  `CURSOR_PLUGIN_NODE=/no-node`.
- The actual library loaded through C ABI v1 via Python ctypes under that same
  environment. Registration, credential parsing, native quota HTTP callbacks,
  error status mapping and callback buffer ownership all passed. Python was
  the test host only; it is not used by the library.
- `go list -deps .` contains neither `os/exec` nor third-party module packages.
  `otool -L` shows only macOS system libraries/frameworks, not libnode or a JS
  engine. macOS Keychain access uses Security/CoreFoundation directly.
- The portable Go core compiled as test binaries for Linux AMD64, Linux ARM64
  and Windows AMD64 using `CGO_ENABLED=0`. Those binaries were not executed;
  this is a core compile check, not a native C ABI build or runtime validation
  for those platforms.

The standard `make test` workflow does not invoke Node, Bun or Python.
`testdata/reference-golden.json` is checked in. The JS reference and optional
fixture regeneration script are developer resources, excluded from the native
library and binary release archive.

No real Cursor credentials were used. Real subscription access, actual proxy
traffic, the CPA frontend and full CPA server routing remain deployment checks.
The underlying host integration continues to use CPA's existing HTTP callbacks
for its global proxy and logging. Per-account proxy overrides still require a
host API enhancement and fail explicitly in this plugin.

This version uses complete Chat history for tool continuations, matching the
prior request-scoped CPA transport. It does not implement the reference's
cross-request native Run retention or deferred dashboard token ledger. Missing
upstream step counters are explicitly marked as estimated; final TurnEnded
counters are preserved.
