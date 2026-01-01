from typing import Optional
from ..common.check import Check
_ffmpeg_path: Optional[str]=None

def get_ffmpeg():
    global _ffmpeg_path
    if _ffmpeg_path is None:
        _ffmpeg_path=Check.ffmpeg()
    return _ffmpeg_path