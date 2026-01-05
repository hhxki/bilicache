"""
配置管理器
"""

from tomlkit import parse, dumps, document, item, nl
import os
import threading

# 跨平台文件锁支持
if os.name == "nt":  # Windows
    import msvcrt
else:  # Unix/Linux
    import fcntl


class ConfigManager:
    def __init__(self, path="./config/config.toml"):
        self.path = path
        self.data = {}
        self._lock = threading.Lock()
        if not os.path.exists(self.path):
            self._create()
        self._load()

    def _ensure_dir(self):
        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    def _create(self):
        if self.path == "./config/config.toml":
            self.data = parse(DEFAULT_CONFIG)
        elif self.path == "./config/creator.toml":
            self.data = parse("#[bilibili.193440430]")
        else:
            self.data = document()
        self._save()

    def _load(self, require_lock=True):
        """加载配置文件"""

        def _do_load():
            try:
                # 文件锁只针对 path，不关心 open 模式
                if os.name == "nt":
                    with open(self.path, "rb") as f:
                        size = os.path.getsize(self.path)
                        if size > 0:
                            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, size)
                        with open(self.path, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                self.data = parse(content)
                            else:
                                self.data = document()
                        if size > 0:
                            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, size)
                else:
                    # Unix: 用独立 fd 上锁
                    with open(self.path, "rb") as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    with open(self.path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            self.data = parse(content)
                        else:
                            self.data = document()

            except (IOError, OSError):
                with open(self.path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.data = parse(content)
                    else:
                        self.data = document()

        if require_lock:
            with self._lock:
                _do_load()
        else:
            _do_load()

    def _save(self, require_lock=True):
        """保存配置文件
        require_lock: 如果为 False，则不在内部获取锁（调用者已持有锁）
        """
        self._ensure_dir()

        def _do_save():
            # 使用临时文件+原子重命名来保证写入安全
            temp_path = self.path + ".tmp"
            # 在 Windows 上，需要先创建文件再锁定
            with open(temp_path, "wb") as f:
                if os.name == "nt":  # Windows
                    # Windows 使用 msvcrt.locking，需要先写入数据才能锁定
                    f.write(dumps(self.data).encode("utf-8"))
                    f.flush()
                    file_size = f.tell()
                    if file_size > 0:
                        f.seek(0)
                        try:
                            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, file_size)
                            f.flush()
                            os.fsync(f.fileno())
                            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, file_size)
                        except (IOError, OSError):
                            # 如果锁定失败，继续执行（至少数据已写入）
                            pass
                else:  # Unix/Linux
                    # Unix/Linux 使用文件锁
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        f.write(dumps(self.data).encode("utf-8"))
                        f.flush()
                        os.fsync(f.fileno())
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            # 原子性替换
            if os.path.exists(self.path):
                os.replace(temp_path, self.path)
            else:
                os.rename(temp_path, self.path)

        if require_lock:
            with self._lock:
                _do_save()
        else:
            # 调用者已持有锁，直接保存
            _do_save()

    def has(self, section, key=None):
        if key is None:
            return section in self.data
        return section in self.data and key in self.data[section]

    def get(self, section, key, default=None):
        return self.data.get(section, {}).get(key, default)

    def get_key(self, section):
        return list(self.data.get(section, {}).keys())

    def set(self, section, key, value):
        self.data.setdefault(section, {})
        self.data[section][key] = value
        self._save()

    def set_batch(self, updates):
        """批量更新配置，减少文件写入次数
        updates: [(section, key, value), ...]
        """
        for section, key, value in updates:
            self.data.setdefault(section, {})
            self.data[section][key] = value
        self._save()

    def equal(self, section, key, value):
        if self.data[section][key] == value:
            return True
        else:
            return False


DEFAULT_CONFIG = """\
#日志设置
[logging]
debug = false

#轮询检查设置
[check]  
#并发检查数
semaphore=10
#轮询时间间隔
sleep=10

#下载设置
[download]
#并发下载数量
semaphore=5

#ffmpeg设置 默认采用环境变量中的ffmpeg 如果没有的话就查找路径中的
[ffmpeg]
#使用环境变量中的ffmpeg
use_env=true
# Windows 路径
path = "./ffmpeg/ffmpeg.exe"
# linux 路径
# path = "/usr/local/bin"

#定时重启间隔
[runtime]
restart_interval=11400

"""
