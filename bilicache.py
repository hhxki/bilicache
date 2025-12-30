import asyncio
import os
from bilibili_api import video, Credential, ResponseCodeException
import aiohttp
from pprint import pprint
import login_cookie
from config_manager import ConfigManager
import subprocess
from creator_manager import CreatorManager
from record_manager import RecordManager
from bilicache_exception import *
import logging

logger = logging.getLogger("bilicache")


def safe_filename(filename: str) -> str:
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
    v = video.Video(bvid=vid_id, credential=credential)
    vid_info = await v.get_info()
    title = safe_filename(vid_info["title"])
    creator = CreatorManager(vid_info["owner"]["mid"])
    path = await creator.get_bilibili_path()
    record = RecordManager(path)
    if record.has(vid_id):
        logging.info(f"存在{vid_id}下载记录，跳过")
        return
    try:
        url = await v.get_download_url(cid=vid_info["cid"])
    except ResponseCodeException as e:
        if e.code == 87008:
            raise ErrorChargeVideo(f"跳过充电视频:{title}")
        raise
    vid_quality_list = url["accept_quality"]
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
                raise ErrorCountTooMuch("下载失败次数过多")
            asyncio.sleep(1)
    retry = 0
    logger.debug(f"下载{vid_id}音频流")
    while True:
        try:
            await downloadAudio(url, vid_quality_list[0], title, path=path)
            break
        except:
            retry += 1
            try:
                os.remove(f"{path}{title}_temp.m4a")
            except:
                pass
            if retry >= 5:
                del retry
                raise ErrorCountTooMuch("下载失败次数过多")
            asyncio.sleep(1)
    logger.debug(f"合并{vid_id}")
    if os.path.exists(f"{path}{title}.mp4"):
        os.remove(f"{path}{title}.mp4")
    DEV_NULL = open(os.devnull, "w")
    subprocess.run(
        (
            "./ffmpeg/ffmpeg",
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
    logger.info(f"{vid_id}合并完成")
    record.add(vid_id, title)
    logger.info(f"添加记录{vid_id}")
