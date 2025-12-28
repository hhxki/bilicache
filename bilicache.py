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


class ErrorCountTooMuch(Exception):
    def __init__(self, info):
        Exception.__init__(self)
        self.info = info

    def __str__(self):
        return self.info


class ErrorChargeVideo(Exception):
    def __init__(self, info):
        Exception.__init__(self)
        self.info = info

    def __str__(self):
        return self.info


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
        print(f"存在{vid_id}下载记录，跳过")
        return
    try:
        url = await v.get_download_url(cid=vid_info["cid"])
    except ResponseCodeException as e:
        if e.code == 87008:
            raise ErrorChargeVideo(f"跳过充电视频:{title}")
        raise
    vid_quality_list = url["accept_quality"]
    print("开始下载视频流")
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
    print("开始下载音频流")
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
    print("开始合并")
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
    print("下载完成")
    record.add(vid_id, title)
    print("添加记录")


async def main() -> None:
    config = ConfigManager()
    if not config.has("account", "cookies"):
        cookies = await login_cookie.get_cookies()
        config.set("account", "cookies", cookies)
    cookies = config.get("account", "cookies")
    credential = Credential(
        sessdata=cookies["SESSDATA"],
        bili_jct=cookies["bili_jct"],
        buvid3=cookies["buvid3"],
        buvid4=cookies["buvid4"],
        dedeuserid=cookies["DedeUserID"],
        ac_time_value=cookies["ac_time_value"],
    )

    creators = CreatorManager.get_bilibili_creator_list()
    for creator in creators:
        videos = await creator.get_bilibili_videos()
        for v in videos:
            try:
                await VideoDown(vid_id=v, credential=credential)
            except ErrorChargeVideo as e:
                print(e)
            except ResponseCodeException as e:
                print(f"{v}其他接口错误:{e.code}")


if __name__ == "__main__":
    if not os.path.exists("./Download"):
        os.mkdir("./Download")
    asyncio.run(main())
