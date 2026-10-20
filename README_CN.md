# CLIProxyAPI Cursor 原生插件

**0.1.0 已改为 Go 原生动态库，不需要 Node.js、Bun、Python 或外部运行脚本。**
Python 仅用于开发时验证 C ABI，不是安装或运行依赖。

参考 magpie-community 的 MIT Cursor 插件移植，使用 CLIProxyAPI 的 C ABI v1。
支持浏览器登录、API Key 凭据、模型发现、流式/非流式回复、图片、推理参数、
工具调用及完整历史续接，并保留 CPA 全局代理、请求日志和额度展示。

## 安装或升级

1. 取出与你的操作系统和 CPU 架构匹配的动态库。
2. 将其放入 CPA 的插件目录，文件名保持 `cursor.dylib` / `cursor.so` / `cursor.dll`。
3. 启用插件并重启 CPA。
4. 在 CPA 中完成 Cursor 登录，或继续使用旧版已经保存的 Cursor 凭据。
5. 从 `/v1/models` 返回的列表中选择 `cursor/<模型名>` 使用。

```yaml
plugins:
  enabled: true
  dir: /你的绝对路径/plugins
  configs:
    cursor:
      enabled: true
      priority: 1
```

当前提供源码，需要在目标平台编译动态库，不附带预编译安装包；
其 Go 核心已经做过 Linux AMD64 / ARM64、Windows AMD64 的交叉编译检查，
这不等于这些平台的动态库已完成实际运行验证。

从 0.2.0 升级时只需替换动态库。原有 `type: cursor`、`cursor_auth` 凭据格式兼容，
无需重新创建凭据。旧版的 `CURSOR_PLUGIN_NODE` 环境变量不再使用。
此插件尚未发布到 CPA 插件商店，目前是本地动态库安装方式。

## 直接在 CPA 中登录

使用 CPA 的插件 OAuth 登录流程，provider 为 `cursor`，不需要额外登录脚本。
若管理界面尚未展示 Cursor 按钮，可以调用当前参考 CPA v8 的管理接口：

```sh
curl 'http://127.0.0.1:8317/v8/management/oauth/auth-url?provider=cursor' \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

打开响应中的 `url`，在浏览器完成授权。随后以响应中的 `state` 查询：

```sh
curl "http://127.0.0.1:8317/v8/management/oauth/status?state=$STATE" \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

在授权完成前定期查询，返回 `status: ok` 后 CPA 会保存凭据。
管理密钥与模型调用使用的客户端 API Key 不是同一用途。
浏览器登录使用 PKCE，令牌到期后需要重新登录；不会假装用 refresh token 自动续期。

已有 Cursor Dashboard API Key 时，也可以在 CPA 导入以下 JSON 凭据文件：

```json
{
  "type": "cursor",
  "cursor_auth": {"type": "api", "key": "YOUR_CURSOR_API_KEY"}
}
```

可选：`auth.login.start` 的 `Metadata.mode` 支持 `cli`，读取同一系统用户已经登录的
cursor-agent 凭据。macOS 通过系统 Security 框架读取钥匙串，其他平台读取对应
`auth.json`；不会启动 cursor-agent 或调用系统命令。CLI 令牌过期后需由用户重新登录。
普通浏览器登录不需要安装 cursor-agent。

## 代理、日志、额度

```yaml
requests:
  proxy-url: "socks5://127.0.0.1:1080"
observability:
  logs:
    request-log: true
```

所有网络请求通过 CPA 的 `host.http.*` 回调发送，没有悄悄退回直连的路径。
因此可沿用 CPA 的全局 HTTP/HTTPS/SOCKS 代理和请求日志。模型发现、认证轮询、
额度读取和 RunSSE/BidiAppend 均走相同接口。

额度通过标准 `quota_provider` 展示套餐、Cursor Models / Other Models 剩余比例、
重置时间，以及可获得的按量付费花费和上限。无限按量付费只展示金额，不伪造剩余额度。

参考 CPA 版本的 HTTP 回调未绑定单账号客户端，所以账号 `proxy_url` 覆盖仍会明确报错；
上游日志可能缺少账号标签，但仍关联原始请求。管理页面额度探测属于管理请求，
不生成普通客户端请求日志。Cursor 上游日志的正文是 Connect/Protobuf 协议数据，
不是自动解码的 Chat JSON。

## 调用与行为

```sh
curl http://127.0.0.1:8317/v1/chat/completions \
  -H "Authorization: Bearer $CPA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"cursor/auto","messages":[{"role":"user","content":"你好"}],"stream":true}'
```

以模型列表实际返回的 ID 为准。其他客户端协议依赖 CPA 的内置转换。
只有调用方提供的工具可以被返回；Cursor 原生的 shell、读文件、写文件等请求会被拒绝，
插件不替用户执行工具。续接时需携带完整的 assistant 工具调用和对应 tool 结果。

CPA 会在请求结束后关闭 HTTP 操作，因此仍使用完整历史重建，不跨请求保留 Cursor Run。
最终回复使用上游 TurnEnded 的 token 计数；没有上游计数的工具调用步骤会明确标记
`usage.cursor_usage_estimated: true`。此版本没有移植 magpie 的延迟账单补记机制。
独立 token 计数、任意 HTTP 转发、重置订阅额度接口返回 501。

## 构建与验证

构建需要 Go 1.23+ 和本机 C 编译器，没有第三方 Go 模块依赖：

```sh
make build
make test
```

macOS 输出 `dist/cursor.dylib`，Linux 输出 `dist/cursor.so`，Windows 输出
`dist/cursor.dll`。Windows 构建需要与 Go 架构匹配的 MinGW C 编译器。
这些是构建工具，使用已经编译好的插件时不需要安装。

验证包括：864 组模型解析对照、会话与 Protobuf 对照、真实 Go 编解码器的
RunSSE/BidiAppend 与工具结果续接模拟联调、取消/错误/并发检查、`-race`、`go vet`，
以及在没有可用 PATH/Node 的环境下加载实际动态库并完成额度回调。
真实 Cursor 账号调用和完整 CPA 服务端路由尚未实测。

完整记录见 [VALIDATION.md](VALIDATION.md)，来源说明见 [NOTICE.md](NOTICE.md)。
旧 Node 代码只保留在 `reference/node-v0.2.0/` 用于对照，不会编译进动态库。
