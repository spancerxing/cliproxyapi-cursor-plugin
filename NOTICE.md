# Source and attribution

The native implementation is based on the Cursor protocol, authentication,
model selection, transcript and quota behavior in
https://github.com/magpie-community/plugins/tree/main/packages/cursor,
`@magpie-community/opencode-cursor-auth` version 0.2.19, retrieved 2026-10-20.
The original MIT copyright and license are preserved in `LICENSE` and under
`reference/node-v0.2.0/vendor/cursor/LICENSE`.

Version 0.1.0 ports production behavior to Go. The native library contains no
JavaScript engine, JavaScript source assets, embedded worker or subprocess
bridge. The historical 0.2.0 reference implementation under `reference/` is
excluded from native builds.

`testdata/reference-golden.json` contains synthetic model, conversation and
protobuf expectations generated from that MIT reference. Native tests read
these checked-in fixtures without running Node or Bun. The developer-only
`scripts/generate-reference-fixtures.mjs` can regenerate them when intentionally
updating the reference. Running that optional development script needs Node;
installing, building, testing and running the native plugin do not.

The native protocol keeps the upstream MCP namespace `magpie` for wire and
transcript compatibility. This does not launch or require the magpie app.
