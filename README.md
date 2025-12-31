# BiliCache

B站视频自动下载缓存工具

## 项目结构

```
bilicache/
├── bilicache/              # 主包目录
│   ├── __init__.py         # 包入口，导出主要API
│   ├── core/               # 核心功能模块
│   │   ├── __init__.py
│   │   └── download.py     # 视频下载核心功能
│   ├── managers/           # 管理器模块
│   │   ├── __init__.py
│   │   ├── config_manager.py    # 配置管理器
│   │   ├── creator_manager.py   # 创作者管理器
│   │   └── record_manager.py    # 下载记录管理器
│   ├── common/             # 通用工具模块
│   │   ├── __init__.py
│   │   ├── exceptions.py  # 自定义异常类
│   │   └── log.py         # 日志处理器
│   ├── api/               # API相关模块
│   │   ├── __init__.py
│   │   ├── login.py       # 登录功能
│   │   └── controller.py  # 异步任务控制器
│   └── config/            # 配置文件目录（运行时生成）
├── config/                 # 配置文件目录
│   ├── config.toml        # 主配置文件
│   └── creator.toml        # 创作者配置
├── Download/              # 下载目录（运行时生成）
├── main.py                # 主程序入口
├── setup.py               # 安装配置
├── pyproject.toml         # 项目配置
└── test/                  # 测试目录
```

## 安装

### 开发模式安装

```bash
pip install -e .
```

### 普通安装

```bash
pip install .
```

## 使用方法

### 直接运行

```bash
python main.py
```

### 作为模块运行

```bash
python -m bilicache
```

## 模块说明

### bilicache.core
核心下载功能，包括视频和音频流的下载、合并等。

### bilicache.managers
各种管理器类：
- `ConfigManager`: 管理TOML配置文件
- `CreatorManager`: 管理B站UP主信息
- `RecordManager`: 管理下载记录

### bilicache.common
通用工具：
- `exceptions`: 自定义异常类
- `log`: 日志处理器

### bilicache.api
API相关功能：
- `login`: B站登录和cookie获取
- `controller`: 异步任务调度和分发

## 开发

### 运行测试

```bash
python -m pytest test/
```

### 代码格式

```bash
black bilicache/
```

## 依赖

- bilibili-api >= 5.0.0
- aiohttp >= 3.8.0
- tomli-w >= 1.0.0

## 许可证

MIT License

