# 夏普扫描到 Mac

首次使用新 Mac 时，请先完成[在另一台 Mac 上配置](#在另一台-mac-上配置)。这台夏普使用 FTP 将扫描件发送到 Mac，无需安装夏普扫描驱动。

在本工作区打开终端，运行 `./src/ftp-cli start`。保持 Mac 唤醒并连接局域网，在夏普 MX-C4082R 上选择「图像发送」→「地址簿」→你的 Mac 对应的目的地（例如「Your Mac」），选择 PDF 并按「开始」。扫描件保存在工作区的 `scans/` 子目录，可用 `open scans` 在访达中查看。

## 日常操作

完成首次配置后，在项目根目录激活虚拟环境，随后可在当前终端的任意目录运行 `ftp-cli`：

```bash
source .venv/bin/activate
ftp-cli status
```

`uv sync --locked` 会把项目命令安装到 `.venv/bin/ftp-cli`。也可以在项目根目录直接运行 `./src/ftp-cli status`。

| 操作 | 命令 |
| --- | --- |
| 后台启动 | `ftp-cli start` |
| 查看状态 | `ftp-cli status` |
| 关闭 | `ftp-cli stop` |
| 重启 | `ftp-cli restart` |
| 查看最近日志并跟踪新记录 | `ftp-cli logs`（Ctrl-C 退出查看） |
| 从本机上传测试文件、核对内容并清理 | `ftp-cli test` |

后台进程由本工作区专用的 tmux 会话托管。关闭终端后可继续接收，重新登录或重启 Mac 后需手动运行 `ftp-cli start`。关闭或重启服务前，请等当前扫描传输完成。

## 扫描仪设置

本机已配置好。查看本工作区使用的服务器 IP、端口、扫描仪 IP 和用户名：

```bash
cat .local/config.toml
```

地址簿中的服务器填 `mac_ip`，端口填 `port`（默认 21），用户名填 `username`（默认 `sharp-scan`）。选择 FTP 并启用 PASV 模式，目录填 `/`，它对应项目中的 `scans/` 目录。密码可用下面的命令复制到剪贴板：

```bash
tr -d '\n' < .local/password | pbcopy
```

换网络后，核对两端的 IP，更新 `.local/config.toml` 并重启服务。如果 Mac 地址变化，还要修改扫描仪地址簿的服务器地址。排查收件问题时可先执行 `./src/ftp-cli test`，再查看日志。来自扫描仪 IP 的 `STOR ... completed=1` 表示该文件已传完。

## 在另一台 Mac 上配置

**1. 准备电脑和网络。** 让新 Mac 和打印机在局域网内互通，记下两台设备各自的局域网 IPv4 地址。以下步骤假设已安装 `uv`。后台运行还需要 `tmux`，缺少时可用 Homebrew 安装（`brew install tmux`）。在想要存放项目的位置打开终端，克隆仓库并进入项目目录：

```bash
git clone https://github.com/YushunXiang/sharp-scan-ftp.git
cd sharp-scan-ftp
```

**2. 初始化项目。** 在项目根目录执行以下命令。`uv sync --locked` 会按项目要求选用 Python 3.12（默认在缺少时自动下载），创建 `.venv` 并按锁文件安装依赖。其余命令生成这台 Mac 的配置和 FTP 密码。

```bash
uv sync --locked
mkdir -p -m 700 .local
cp -n config.example.toml .local/config.toml
(umask 077; set -C; openssl rand -hex 14 > .local/password)
```

**3. 启动并自测。** 编辑 `.local/config.toml`，将 `mac_ip` 改为新 Mac 的局域网 IP，将 `scanner_ip` 改为打印机的 IP。保存后执行：

```bash
./src/ftp-cli start
./src/ftp-cli test
```

**4. 从打印机试扫一页。** 在打印机地址簿中新增目的地，例如「Your Mac」，按[扫描仪设置](#扫描仪设置)填写新 Mac 的连接信息。保持 Mac 唤醒，在打印机上选择「图像发送」→「地址簿」→「Your Mac」，选择 PDF 并按「开始」。在项目根目录运行 `open scans`，确认收到刚扫描的 PDF。

以后重新登录或重启 Mac 后，在项目根目录运行 `./src/ftp-cli start` 即可恢复接收。维护现有工作区依赖时，运行 `uv sync --locked`，然后重启服务。

## 项目文件与本机数据

- [src/ftp-cli](src/ftp-cli) 提供日常管理命令，[sharp_scan_ftp](src/sharp_scan_ftp/) 包含接收服务、命令行入口和上传自测。
- [config.example.toml](config.example.toml) 提供配置模板。[pyproject.toml](pyproject.toml) 和 [uv.lock](uv.lock) 记录项目依赖。
- `.local/` 保存实际配置、密码、日志和运行时套接字。`.venv/` 是项目虚拟环境，包含项目命令和依赖。
- FTP 账号仅能访问 `scans/` 顶层的扫描文件类型，包括 PDF、常用图像格式和扫描仪支持的文档格式。项目代码和本机配置不在 FTP 可见范围内。
- [.gitignore](.gitignore) 排除 `scans/`、本机配置、解释器及构建产物。源码、文档、配置模板和依赖清单可以直接纳入版本控制。
