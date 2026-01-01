"""
BiliCache - B站视频自动下载缓存工具
"""

__version__ = "1.0.0"

from .core.download import VideoDown
from .managers.config_manager import ConfigManager
from .managers.creator_manager import CreatorManager
from .managers.record_manager import RecordManager
from .api.controller import poller, dispatcher, DownloadEvent
from .common.exceptions import ErrorCountTooMuch, ErrorChargeVideo
from .common.check import Check
from .config.ffmpeg_locator import get_ffmpeg
from .config.cookies_locator import get_credential, init_credential

__all__ = [
    "VideoDown",
    "ConfigManager",
    "CreatorManager",
    "RecordManager",
    "poller",
    "dispatcher",
    "DownloadEvent",
    "ErrorCountTooMuch",
    "ErrorChargeVideo",
    "ErrorNoAudioStream",
    "Check",
    "get_credential",
    "init_credential",
]

import logging
import sys

LOG_CONF = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(filename)s[line:%(lineno)d](Pid:%(process)d "
            "Tname:%(threadName)s) %(levelname)s %(message)s",
            # 'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(filename)s%(lineno)d[%(levelname)s]Tname:%(threadName)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": logging.DEBUG,
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "simple",
        },
        "file": {
            "level": logging.DEBUG,
            "class": "bilicache.common.log.SafeRotatingFileHandler",
            "when": "W0",
            "interval": 1,
            "backupCount": 1,
            "filename": "ds_update.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": logging.INFO,
    },
    "loggers": {
        "bilicache": {
            "handlers": ["file"],
            "level": logging.INFO,
        },
    },
}
