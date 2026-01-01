"""
BiliCache - B站视频自动下载缓存工具
"""

__version__ = "1.0.0"

from bilicache.core.download import VideoDown
from bilicache.managers.config_manager import ConfigManager
from bilicache.managers.creator_manager import CreatorManager
from bilicache.managers.record_manager import RecordManager
from bilicache.api.controller import poller, dispatcher, DownloadEvent
from bilicache.common.exceptions import ErrorCountTooMuch, ErrorChargeVideo
from bilicache.common.check import Check
from bilicache.config.ffmpeg_locator import get_ffmpeg
from bilicache.config.cookies_locator import get_credential, init_credential

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
