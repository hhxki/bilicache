import aiohttp
from pathlib import Path
import os
import shutil
import platform
from bilicache.managers.config_manager import ConfigManager
import logging

logger = logging.getLogger("bilicache")


class Check:
    def __init__(self):
        pass
    @staticmethod
    def ffmpeg() -> str:
        """
        查找 ffmpeg 可执行文件路径
        优先级：
        1. 环境变量 PATH
        2. 配置文件中的 ffmpeg 路径
        3. 提示用户安装 ffmpeg
        """
        config = ConfigManager()
        system = platform.system().lower()
        ffmpeg_name = "ffmpeg.exe" if system == "windows" else "ffmpeg"
        if config.get("ffmpeg", "use_env"):
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                logger.debug(f"[ffmpeg] 使用环境变量: {ffmpeg_path}")
                return ffmpeg_path

        try:
            cfg_path = config.get("ffmpeg", "path")
        except Exception:
            cfg_path = None

        if cfg_path:
            cfg_path = os.path.expanduser(cfg_path)

            if os.path.isfile(cfg_path):
                logger.debug(f"[ffmpeg] 使用固定路径: {cfg_path}")
                return cfg_path

            candidate = os.path.join(cfg_path, ffmpeg_name)
            if os.path.isfile(candidate):
                logger.debug(f"[ffmpeg] 使用固定路径: {candidate}")
                return candidate
        raise FileNotFoundError(
            "未找到 ffmpeg：\n"
            "1. 环境变量 PATH 中不存在 ffmpeg\n"
            "2. 配置文件中未正确指定 ffmpeg 路径\n\n"
            "请安装 ffmpeg 并确保：\n"
            "- Windows: https://ffmpeg.org/download.html\n"
            "- Linux: sudo apt install ffmpeg / sudo yum install ffmpeg"
        )

    @staticmethod
    async def network(timeout=3):
        """检查网络连接"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://www.baidu.com", timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    @staticmethod
    def tempfile(root_dir: str):
        """检查临时文件并删除"""
        root = Path(root_dir)
        if not root.exists():
            raise FileNotFoundError(f"目录不存在: {root}")
        for file in root.rglob("*"):
            if file.is_file() and "_temp" in file.stem:
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"删除失败: {file} | {e}")
