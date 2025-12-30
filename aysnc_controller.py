from dataclasses import dataclass
import asyncio
from bilicache_exception import *
import bilicache
import logging
from bilibili_api import ResponseCodeException
from creator_manager import CreatorManager
from record_manager import RecordManager


@dataclass
class DownloadEvent:
    vid_id: str
    credential: object


logger = logging.getLogger("bilicache")


async def poller(queue: asyncio.Queue, credential):
    while True:
        creators = CreatorManager.get_bilibili_creator_list()
        sem = asyncio.Semaphore(5)
        tasks = [
            process_creator(creator, queue, credential, sem) for creator in creators
        ]
        await asyncio.gather(*tasks)
        await asyncio.sleep(10)


async def process_creator(creator, queue, credential, sem: asyncio.Semaphore):
    async with sem:
        videos = await creator.get_bilibili_videos()
        path = await creator.get_bilibili_path()
        record = RecordManager(path)
        videos = record.filter_videos(videos)
        creator_name = await creator.get_bilibili_name()
        if not videos:
            logging.info(f"{creator_name}:未检测到新视频")
        for vid in videos:
            event = DownloadEvent(vid_id=vid, credential=credential)
            await queue.put(event)


async def handle_download(event: DownloadEvent, sem: asyncio.Semaphore):
    async with sem:
        try:
            await bilicache.VideoDown(vid_id=event.vid_id, credential=event.credential)
        except ErrorChargeVideo as e:
            logger.exception(e)
        except ResponseCodeException as e:
            logger.exception(f"{event.video_id} 接口错误: {e.code}")


async def _run(event, queue, sem):
    try:
        await handle_download(event, sem)
    finally:
        queue.task_done()


async def dispatcher(queue: asyncio.Queue, sem: asyncio.Semaphore):
    while True:
        event = await queue.get()
        asyncio.create_task(_run(event, queue, sem))
