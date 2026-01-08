"""
视频下载核心功能
"""

import asyncio
import os
from bilibili_api import video, ResponseCodeException
import aiohttp
import subprocess
import logging

from ..managers.creator_manager import CreatorManager
from ..managers.record_manager import RecordManager
from ..common.exceptions import (
    ErrorCountTooMuch,
    ErrorChargeVideo,
    ErrorNoAudioStream,
)
from ..config.ffmpeg_locator import get_ffmpeg
from ..config.cookies_locator import get_credential
from ..common.check import Check

logger = logging.getLogger("bilicache")


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


async def VideoDown(vid_id: str):
    """下载视频的主函数"""
    v = video.Video(bvid=vid_id, credential=get_credential())
    vid_info = await v.get_info()
    creator = CreatorManager(vid_info["owner"]["mid"])
    name = await creator.get_bilibili_name()
    path = await creator.get_bilibili_path()
    title = Check.safe_filename(vid_info["title"])
    filename = f"{title}-{vid_id}"
    video_log = f"{vid_id}: {name} - {title}"
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

    logger.info(f"开始下载 {video_log}")

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
            # 添加充电视频记录
            logger.info(f"充电视频 跳过{video_log}")
            record.add_charge(vid_id, title)
        raise
    vid_quality_list = url["accept_quality"]
    try:
        logger.debug(f"下载视频流 {video_log}")
        retry = 0
        while True:
            try:
                await downloadVideo(url, vid_quality_list[0], filename, path=path)
                break
            except:
                if vid_info.get("is_upower_exclusive", False):
                    logger.info(f"充电视频 跳过{video_log}")
                    record.add_charge(vid_id, title)
                    return
                retry += 1
                try:
                    os.remove(f"{path}{filename}_temp.mp4")
                except:
                    pass
                if retry >= 5:
                    del retry
                    logger.debug(f"下载{vid_id}视频失败")
                    raise ErrorCountTooMuch("下载失败次数过多")
                await asyncio.sleep(1)
        retry = 0
        logger.debug(f"下载音频流 {video_log}")
        while True:
            try:
                await downloadAudio(url, vid_quality_list[0], filename, path=path)
                break
            except ErrorNoAudioStream:
                logger.debug(f"{vid_id} 无音频流，跳过音频下载")
                os.replace(f"{path}{filename}_temp.mp4", f"{path}{filename}.mp4")
                record.add(vid_id, title)
                logger.debug(f"添加记录 {video_log}")
                return
            except Exception:
                retry += 1
                try:
                    os.remove(f"{path}{filename}_temp.m4a")
                except:
                    pass
                if retry >= 5:
                    del retry
                    logger.debug(f"下载音频失败 {video_log}")
                    raise ErrorCountTooMuch("下载失败次数过多")
                await asyncio.sleep(1)
        logger.debug(f"合并{vid_id}")
        if os.path.getsize(f"{path}{filename}_temp.mp4") == 0:
            raise RuntimeError("视频流为空，拒绝合并")
        proc = await asyncio.create_subprocess_exec(
            get_ffmpeg(),
            "-y",
            "-i",
            f"{path}{filename}_temp.mp4",
            "-i",
            f"{path}{filename}_temp.m4a",
            "-vcodec",
            "copy",
            "-acodec",
            "copy",
            f"{path}{filename}.mp4",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        os.remove(f"{path}{filename}_temp.mp4")
        os.remove(f"{path}{filename}_temp.m4a")
        logger.info(f"合并完成 {video_log}")
        # add 方法会自动取消 downloading 状态并添加到完成记录
        record.add(vid_id, title)
        logger.debug(f"添加记录 {video_log}")

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
        try:
            os.remove(f"{path}{title}.mp4")
        except:
            pass
        raise
