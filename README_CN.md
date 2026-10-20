# CLIProxyAPI Cursor 插件

将 Cursor 接入 CLIProxyAPI，支持流式回复、图片、工具调用和额度展示，沿用 CPA 的全局代理与请求日志。
Go 原生插件，运行时无需 Node.js。

[English](README.md)

## 构建

需要 Go 1.23+、C 编译器和 Make。在与 CPA 相同的系统、CPU 架构下执行：

```sh
git clone https://github.com/spancerxing/cliproxyapi-cursor-plugin.git
cd cliproxyapi-cursor-plugin
make build
```

产物位于 `dist/`：Linux 为 `cursor.so`，Windows 为 `cursor.dll`，macOS 为 `cursor.dylib`。
Windows 构建需要匹配架构的 MinGW 工具链。

## 安装到 CPA

CPA 需要支持 C ABI v1 插件。将动态库放入插件目录，并在 CPA 配置中启用：

```yaml
plugins:
  enabled: true
  dir: /opt/cpa/plugins
  configs:
    cursor:
      enabled: true
      priority: 1
```

将 `dir` 改为实际路径，重启 CPA 后检查加载日志。Docker 部署需挂载插件目录，配置填写容器内路径。
当前提供源码；仅放入源码或填写 GitHub 地址不会加载插件。

## 登录

在 CPA 中选择 Cursor 登录。若界面没有入口，可使用 CPA v8 管理接口：

```sh
curl 'http://127.0.0.1:8317/v8/management/oauth/auth-url?provider=cursor' \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

打开返回的 `url` 完成授权，再用返回的 `state` 查询，直到 `status` 为 `ok`：

```sh
curl "http://127.0.0.1:8317/v8/management/oauth/status?state=$STATE" \
  -H "Authorization: Bearer $CPA_MANAGEMENT_KEY"
```

也可在 CPA 导入 Cursor Dashboard API Key 凭据：

```json
{
  "type": "cursor",
  "cursor_auth": {"type": "api", "key": "YOUR_CURSOR_API_KEY"}
}
```

## 使用

从 CPA 的 `/v1/models` 获取模型 ID，在客户端选择对应的 `cursor/…` 模型。
浏览器登录令牌过期后需重新登录；暂不支持单账号代理覆盖。

## 开发

```sh
make test
```

验证范围与限制见 [VALIDATION.md](VALIDATION.md)。真实 Cursor 账号和完整 CPA 联调尚未验证。
参考 [magpie Cursor 插件](https://github.com/magpie-community/plugins/tree/main/packages/cursor) 移植，采用 MIT 许可证，来源见 [NOTICE.md](NOTICE.md)。
