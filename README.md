# CLIProxyAPI Cursor Plugin

Connect Cursor to CLIProxyAPI with streaming, images, tool calls and quota reporting.
Uses CPA's global proxy and request logging. Native Go plugin; no Node.js runtime required.

[中文说明](README_CN.md)

## Build

Requires Go 1.23+, a C compiler and Make. Build on the same OS and CPU architecture as CPA:

```sh
git clone https://github.com/spancerxing/cliproxyapi-cursor-plugin.git
cd cliproxyapi-cursor-plugin
make build
```

Output in `dist/`: `cursor.so` on Linux, `cursor.dll` on Windows, or `cursor.dylib` on macOS.
Windows builds require a matching MinGW toolchain.

## Install in CPA

CPA must support C ABI v1 plugins. Copy the library into the plugin directory and enable it in CPA's configuration:

```yaml
plugins:
  enabled: true
  dir: /opt/cpa/plugins
  configs:
    cursor:
      enabled: true
      priority: 1
```

Set `dir` to the actual path, restart CPA and check its loading logs.
For Docker, mount the plugin directory and use its container path.
Only source is provided; CPA cannot load the source directory or a GitHub URL directly.

## Sign in

Choose Cursor login in CPA. If the UI has no entry, use CPA's v8 management API:

```sh
curl 'http://127.0.0.1:8317/v8/management/oauth/auth-url?provider=cursor' \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

Open the returned `url` to authorize, then poll with the returned `state` until `status` is `ok`:

```sh
curl "http://127.0.0.1:8317/v8/management/oauth/status?state=$STATE" \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

Alternatively, import a Cursor Dashboard API Key credential into CPA:

```json
{
  "type": "cursor",
  "cursor_auth": {"type": "api", "key": "YOUR_CURSOR_API_KEY"}
}
```

## Use

Get model IDs from CPA's `/v1/models` and select a `cursor/…` model in your client.
Browser tokens require signing in again after expiry. Per-account proxy overrides are currently unsupported.

## Development

```sh
make test
```

See [VALIDATION.md](VALIDATION.md) for verification scope and limitations.
Real Cursor accounts and full CPA integration have not yet been tested.
Based on the MIT-licensed [magpie Cursor plugin](https://github.com/magpie-community/plugins/tree/main/packages/cursor); see [NOTICE.md](NOTICE.md) for attribution.
