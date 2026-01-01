"""
视频下载核心功能
"""

import asyncio
import os
from bilibili_api import video, Credential, ResponseCodeException
import aiohttp
import subprocess
import logging

from bilicache.managers.creator_manager import CreatorManager
from bilicache.managers.record_manager import RecordManager
from bilicache.common.exceptions import (
    ErrorCountTooMuch,
    ErrorChargeVideo,
    ErrorNoAudioStream,
)
from bilicache.config.ffmpeg_locator import get_ffmpeg

logger = logging.getLogger("bilicache")


def safe_filename(filename: str) -> str:
    """将文件名中的非法字符替换为下划线"""
    return (
        filename.replace("\\", "_")
        .replace("/", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )


async def downloadVideo(url, id, filename, path="./Download/"):
    """下载视频流"""
    async with aiohttp.ClientSession() as sess:
        video_url = url["dash"]["video"][0]["baseUrl"]
        for i in url["dash"]["video"]:
            if i["codecid"] == 7:
                if i["id"] == id:
                    video_url = i["baseUrl"]
        HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
        async with sess.get(video_url, headers=HEADERS) as resp:
            with open(f"{path}{filename}_temp.mp4", "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        f.close()
                        await sess.close()
                        break
                    f.write(chunk)


async def downloadAudio(url, id, filename, path="./Download/"):
    """下载音频流"""
    if not url["dash"]["audio"]:
        logger.debug("抛出无音频流异常")
        raise ErrorNoAudioStream("无音频流")
    async with aiohttp.ClientSession() as sess:
        audio_url = url["dash"]["audio"][0]["baseUrl"]

        for i in url["dash"]["audio"]:
            if i["codecid"] == 7:
                if i["id"] == id:
                    audio_url = i["baseUrl"]
        HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
        async with sess.get(audio_url, headers=HEADERS) as resp:
            with open(f"{path}{filename}_temp.m4a", "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        f.close()
                        await sess.close()
                        break
                    f.write(chunk)


async def VideoDown(vid_id: str, credential=None):
    """下载视频的主函数"""
    v = video.Video(bvid=vid_id, credential=credential)
    vid_info = await v.get_info()
    title = safe_filename(vid_info["title"])
    creator = CreatorManager(vid_info["owner"]["mid"])
    path = await creator.get_bilibili_path()
    record = RecordManager(path)

    # 检查是否已下载完成
    if record.has(vid_id):
        logging.info(f"存在{vid_id}下载记录，跳过")
        return

    if record.is_downloading(vid_id, title):
        logging.info(f"{vid_id}正在下载中，跳过")
        return

    if not record.mark_downloading(vid_id, title):
        logging.info(f"{vid_id}已被其他任务标记为下载中，跳过")
        return

    logger.info(f"开始下载 {vid_id}: {title}")

    try:
        url = await v.get_download_url(cid=vid_info["cid"])
    except ResponseCodeException as e:
        # 如果获取下载链接失败，取消下载中标记
        with record.config._lock:
            record.config._load(require_lock=False)
            downloading = record.config.get("download", "downloading") or {}
            if vid_id in downloading:
                del downloading[vid_id]
                record.config.data.setdefault("download", {})
                record.config.data["download"]["downloading"] = downloading
                record.config._save(require_lock=False)
        if e.code == 87008:
            raise ErrorChargeVideo(f"跳过充电视频:{title}")
        raise
    vid_quality_list = url["accept_quality"]
    try:
        logger.debug(f"下载{vid_id}视频流")
        retry = 0
        while True:
            try:
                await downloadVideo(url, vid_quality_list[0], title, path=path)
                break
            except:
                retry += 1
                try:
                    os.remove(f"{path}{title}_temp.mp4")
                except:
                    pass
                if retry >= 5:
                    del retry
                    logger.debug(f"下载{vid_id}视频失败")
                    raise ErrorCountTooMuch("下载失败次数过多")
                await asyncio.sleep(1)
        retry = 0
        logger.debug(f"下载{vid_id}音频流")
        while True:
            try:
                await downloadAudio(url, vid_quality_list[0], title, path=path)
                break
            except ErrorNoAudioStream:
                logger.debug(f"{vid_id} 无音频流，跳过音频下载")
                os.replace(f"{path}{title}_temp.mp4", f"{path}{title}.mp4")
                record.add(vid_id, title)
                logger.debug(f"添加记录 {vid_id}: {title}")
                return
            except Exception:
                retry += 1
                try:
                    os.remove(f"{path}{title}_temp.m4a")
                except:
                    pass
                if retry >= 5:
                    del retry
                    logger.debug(f"下载{vid_id}音频失败")
                    raise ErrorCountTooMuch("下载失败次数过多")
                await asyncio.sleep(1)
        logger.debug(f"合并{vid_id}")
        if os.path.exists(f"{path}{title}.mp4"):
            os.remove(f"{path}{title}.mp4")
        DEV_NULL = open(os.devnull, "w")

        subprocess.run(
            (
                get_ffmpeg(),
                "-i",
                f"{path}{title}_temp.mp4",
                "-i",
                f"{path}{title}_temp.m4a",
                "-vcodec",
                "copy",
                "-acodec",
                "copy",
                f"{path}{title}.mp4",
            ),
            stdout=DEV_NULL,
            stderr=subprocess.STDOUT,
        )
        DEV_NULL.close()
        del DEV_NULL
        os.remove(f"{path}{title}_temp.mp4")
        os.remove(f"{path}{title}_temp.m4a")
        logger.info(f"合并完成 {vid_id}: {title}")
        # add 方法会自动取消 downloading 状态并添加到完成记录
        record.add(vid_id, title)
        logger.debug(f"添加记录 {vid_id}: {title}")

    except Exception as e:
        # 下载失败时，清理 downloading 状态和临时文件
        # 使用锁保护下的原子操作
        with record.config._lock:
            record.config._load(require_lock=False)
            downloading = record.config.get("download", "downloading") or {}
            if vid_id in downloading:
                del downloading[vid_id]
                record.config.data.setdefault("download", {})
                record.config.data["download"]["downloading"] = downloading
                record.config._save(require_lock=False)
        try:
            os.remove(f"{path}{title}_temp.mp4")
        except:
            pass
        try:
            os.remove(f"{path}{title}_temp.m4a")
        except:
            pass
        raise
