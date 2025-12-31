"""
BiliCache - B站视频自动下载缓存工具
"""

__version__ = "1.0.0"

from bilicache.core.download import VideoDown, safe_filename
from bilicache.managers.config_manager import ConfigManager
from bilicache.managers.creator_manager import CreatorManager
from bilicache.managers.record_manager import RecordManager
from bilicache.api.login import get_cookies
from bilicache.api.controller import poller, dispatcher, DownloadEvent
from bilicache.common.exceptions import ErrorCountTooMuch, ErrorChargeVideo

__all__ = [
    "VideoDown",
    "safe_filename",
    "ConfigManager",
    "CreatorManager",
    "RecordManager",
    "get_cookies",
    "poller",
    "dispatcher",
    "DownloadEvent",
    "ErrorCountTooMuch",
    "ErrorChargeVideo",
]

