# Native Cursor plugin for CLIProxyAPI

Version **0.1.0** is a Go C ABI dynamic library. **No Node.js, Bun, Python,
external scripts, helper processes, or third-party Go modules are required at
runtime.** Python is used only for the optional development ABI test.

This is a native port of the MIT-licensed magpie-community Cursor provider,
using the C ABI v1 and schema-v1 capability interface in the CPA v8 main
snapshot retrieved on 2026-10-20. The protocol uses Cursor's existing
RunSSE/BidiAppend path through CPA's host HTTP callbacks.

[中文安装说明](README_CN.md)

## Install

Copy the platform's library into CPA's plugin directory:

- macOS: `cursor.dylib`
- Linux: `cursor.so`
- Windows: `cursor.dll`

Enable the plugin and restart CPA:

```yaml
plugins:
  enabled: true
  dir: /absolute/path/to/plugins
  configs:
    cursor:
      enabled: true
      priority: 1
```

Build the dynamic library from source on the target platform. Prebuilt binaries
are not included.
The portable Go core also passes compile checks for Linux AMD64/ARM64 and
Windows AMD64; those checks do not validate the native ABI on those systems.
The plugin has not been published to a store registry.

Upgrading from 0.2.0 requires replacing the library. Existing nested
`cursor_auth` credentials remain compatible. `CURSOR_PLUGIN_NODE` is unused.

## Sign in within CPA

Use CPA's plugin OAuth flow for provider `cursor`. No login script is needed.
If the frontend does not expose a Cursor button, use the reference host's
v8 management API:

```sh
curl 'http://127.0.0.1:8317/v8/management/oauth/auth-url?provider=cursor' \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

Open the returned `url`, authorize in the browser, and poll the returned
`state` until CPA saves the credential:

```sh
curl "http://127.0.0.1:8317/v8/management/oauth/status?state=$STATE" \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

Browser login uses PKCE. Cursor browser access tokens require signing in
again when expired; the plugin does not pretend conventional token refresh
is available.

Existing dashboard API keys can be imported as a CPA credential JSON file:

```json
{
  "type": "cursor",
  "cursor_auth": {"type": "api", "key": "YOUR_CURSOR_API_KEY"}
}
```

OAuth records use nested `type: oauth`, `access`, `refresh`, and `expires`
(Unix milliseconds; 0 defers to JWT expiry), retaining the prior format.
Optional plugin login `Metadata.mode=cli` reads the current OS user's existing
cursor-agent sign-in. macOS uses the Security framework directly; other
platforms use the CLI auth file. No command is spawned. Expired CLI tokens
must be renewed by the user. Browser login does not require cursor-agent.

## Proxy, logs and quota

```yaml
requests:
  proxy-url: "socks5://127.0.0.1:1080"
observability:
  logs:
    request-log: true
```

All upstream HTTP operations use `host.http.*`, inheriting CPA's global
HTTP/HTTPS/SOCKS proxy and request logging. There is no fallback to direct
networking if callbacks are unavailable. Cancellation closes outstanding
operations, response readers and streams, including silent reads.

CPA's standard `quota_provider` integration supplies the plan, included
Cursor Models / Other Models windows, reset times, and available on-demand
spending and limits. Unlimited spending is represented as money, rather than
an invented remaining fraction. Unavailable quota readings fail explicitly.

The referenced host's C ABI HTTP callback does not bind the selected account's
HTTP client. Per-account `proxy_url` overrides therefore fail explicitly;
upstream log entries may omit account labels but retain request context.
Management quota probes do not create ordinary model-request logs. Protocol
request bodies in upstream logs are Connect/Protobuf bytes, not decoded Chat.

## Model behavior

Discover exact `cursor/<upstream-id>` names through `/v1/models`. The native
executor speaks Chat Completions; other client formats depend on CPA's
installed translation capabilities.

The port handles model context/effort/fast variants, Max Mode, inline image
history, reasoning content, caller tools, tool result history and Connect
stream errors. Cursor-native shell/filesystem/approval requests are refused.
Tool execution remains the downstream client's responsibility.

CPA HTTP operations are request-scoped. Tool continuations reconstruct a new
Run from the caller's full Chat history, including assistant calls and tool
results, rather than retaining a transport after CPA closes its scope.
Authoritative TurnEnded counters are used for final replies. Steps without
upstream counters explicitly carry `usage.cursor_usage_estimated: true`.
The reference's deferred dashboard usage ledger is not implemented in this
port. Token counting, arbitrary HTTP forwarding and quota reset return 501.

## Build and test

Build on the target OS/architecture with Go 1.23+, a C compiler and CGO:

```sh
make build
make test
```

Windows needs a matching MinGW toolchain. These build tools are not runtime
dependencies. Core tests and builds do not execute any JavaScript.

Optional ABI verification on macOS:

```sh
python3 test/abi-smoke.py dist/cursor.dylib
```

See [VALIDATION.md](VALIDATION.md) for exact evidence and limits. Real Cursor
credentials and complete CPA server routing have not been tested here.

[NOTICE.md](NOTICE.md) documents attribution. The prior JS implementation is
kept under `reference/node-v0.2.0/` for comparison and fixture regeneration;
it is not embedded, compiled or loaded by the plugin.
