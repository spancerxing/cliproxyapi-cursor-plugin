# 发布

插件 ID 为 `spancerxing-cursor`，登录 provider 和模型前缀为 `cursor`。
官方索引已存在其他作者的 `cursor` 插件，因此使用独立 ID。

## Release

每次推送和 PR 会构建 Linux AMD64、Linux ARM64、Windows AMD64 包；不生成 macOS 包。
Linux 使用 manylinux2014 工具链，目标为 glibc 2.17+，适用于官方 Debian Bookworm Docker 镜像。
不提供 Alpine/musl 安装包。

正式发布前同步修改 `runtime.go` 和 `registry.json` 中的版本，再提交并推送：

```sh
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions 会执行测试、各平台 C ABI 加载、ZIP 格式检查，并发布：

```text
spancerxing-cursor_0.1.0_linux_amd64.zip
spancerxing-cursor_0.1.0_linux_arm64.zip
spancerxing-cursor_0.1.0_windows_amd64.zip
checksums.txt
```

版本标签必须匹配代码和索引。仅推送代码、手动运行工作流不会创建 Release。
工作流使用仓库自带的 `GITHUB_TOKEN`，无需将个人令牌写入文件。
若标签构建失败，修复后先确认该版本尚未发布，再按仓库版本管理流程重试；不会自动覆盖已有 Release。

## 官方商城索引

Release 成功发布后，用有权创建 fork 和 PR 的 GitHub 令牌设置环境变量 `GH_TOKEN`。
先预览，再提交：

```sh
python3 scripts/submit-store-pr.py
python3 scripts/submit-store-pr.py --submit
```

脚本会检查最新正式 Release、平台包及校验清单，fork 官方商城仓库，
创建独立分支，只修改 `registry.json` 并提交 PR。若 ID 或仓库已经收录则停止。
官方审核合并后，默认商城才能展示。网络或认证失败不会视为提交成功。

官方格式说明：<https://github.com/router-for-me/CLIProxyAPI-Plugins-Store#adding-a-plugin>
