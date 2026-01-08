# BiliCache

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**BiliCache** 是一个自动化的 B站视频下载工具，支持监控指定UP主的新视频并自动下载缓存。适合需要离线观看或备份视频内容的用户。

本人有重度赛博仓鼠囤积症，互联网上的数据太过于脆弱了。我实在是见不得昨天收藏的好康的视频今天失效了。前天关注的小姐姐账号已注销。但是在网上找了一圈也没有全自动下载的程序，所以之只能自己去做一个了。

以后有时间会拓展多平台的视频，毕竟抖音上好康的视频也挺多的哈哈哈

## ✨ 特性

- 🎯 **自动监控**：自动检测关注的UP主新发布的视频
- 🎨 **文件管理**：按UP主自动分类存储，文件名智能处理
- 🔐 **多种登录**：支持二维码、账号密码、短信验证码登录
- ⚙️ **配置灵活**：通过 TOML 配置文件自定义各项参数
- 🚀 **后台运行**：支持 daemon 模式，适合 Linux 服务器部署

## 📋 系统要求

- Python 3.9 或更高版本
- FFmpeg（用于视频和音频合并）

### FFmpeg 安装

**Windows:**
- 下载：https://ffmpeg.org/download.html
- 或使用包管理器：`choco install ffmpeg` / `scoop install ffmpeg`

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## 🚀 安装

### 从 PyPI 安装

```bash
pipx install bilicache
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/bilicache.git
cd bilicache

# 安装依赖
pip install -e .
```



## 📖 快速开始

### 1. 启动服务

```bash
# 启动后台服务
bilicache start

# 如果没启动成功可以去这里排查一下
# 日志文件位置：~/.cache/bilicache/.bilicache.log
```

首次运行,程序会自动在 `./config/` 目录下生成默认配置。

### 2. 登录 B站账号

```bash
bilicache login
```
登录获取更清晰的视频，默认选择能获取到的分辨率最高的视频进行下载


支持三种登录方式：
- **二维码登录**（推荐）：在终端扫描二维码
- **账号密码登录**：输入用户名和密码
- **短信验证码登录**：使用手机号登录

### 3. 配置要监控的UP主

编辑 `config/creator.toml` 文件，添加要监控的UP主 UID：

```toml
[bilibili.up主uid]
```
可以在服务运行时添加，会自动生成name。防止后续改名造成文件夹混乱。


### 4. 停止服务

```bash
bilicache stop
```

## ⚙️ 配置说明

### 主配置文件 (`config/config.toml`)

```toml
# 日志设置
[logging]
debug = false  # 是否开启调试日志

# 轮询检查设置
[check]
semaphore = 10  # 并发检查UP主数量
sleep = 60      # 轮询间隔（秒）

# 下载设置
[download]
semaphore = 5   # 并发下载数量

# FFmpeg 设置
[ffmpeg]
use_env = true  # 优先使用环境变量中的 ffmpeg
path = "./ffmpeg/ffmpeg.exe"  # 或指定固定路径

# 运行时设置
[runtime]
restart_interval = 11400  # 定时重启间隔（秒）
```

### UP主配置文件 (`config/creator.toml`)

```toml
[bilibili.193440430]
name="hhxki" #name可以自己随便起名，不写会自动获取

[bilibili.其他up主的uid]
```


## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [bilibili-api-python](https://github.com/nemo2011/bilibili-api) - B站 API 封装
- [tomlkit](https://github.com/python-poetry/tomlkit) - TOML 文件处理
- [biliup](https://github.com/biliup/biliup) - 参考早期操作方式。
- 三年前，为了给喜欢的主播录播。我第一次接触linux系统和服务器，笨拙的启动了biliup。打开了新世界的大门。觉得这个biliup真好用，特别的简单易上手，自己以后也要做一个类似的项目。熟悉biliup的人可以看出来这个项目的风格跟早期的biliup特别相似。可以说没有biliup就没有这个项目，真的是红豆泥阿里嘎多。

## 📮 反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**注意**：本工具仅供学习交流使用，请遵守 B站服务条款，不要用于商业用途或大规模下载。

