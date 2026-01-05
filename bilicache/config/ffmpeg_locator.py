from typing import Optional
from ..common.check import Check

_ffmpeg_path: Optional[str] = None


def get_ffmpeg():
    if _ffmpeg_path is None:
        raise RuntimeError("请先初始化ffmpeg")
    return _ffmpeg_path


def init_ffmpeg():
    global _ffmpeg_path
    _ffmpeg_path = Check.ffmpeg()
