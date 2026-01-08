"""
异步任务控制器
"""

from dataclasses import dataclass
import asyncio
import logging
import aiohttp
from bilibili_api import ResponseCodeException

from ..core.download import VideoDown
from ..managers.creator_manager import CreatorManager
from ..managers.record_manager import RecordManager
from ..managers.config_manager import ConfigManager
from ..common.exceptions import ErrorChargeVideo
from ..common.check import Check


@dataclass
class DownloadEvent:
    vid_id: str


logger = logging.getLogger("bilicache")


async def poller(queue: asyncio.Queue):
    """轮询检查新视频并加入下载队列"""
    while True:
        try:
            if not await Check.network():
                logger.warning("网络未连接,30s后重连")
                await asyncio.sleep(30)
                continue
            creators = CreatorManager.get_bilibili_creator_list()
            config = ConfigManager()
            sem = asyncio.Semaphore(config.get("check", "semaphore"))
            tasks = [process_creator(creator, queue, sem) for creator in creators]
            # 使用 return_exceptions=True 避免单个任务异常导致整个 gather 失败
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 检查是否有异常
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"处理创作者任务 {i} 时发生异常: {result}")
            await asyncio.sleep(config.get("check", "sleep"))
        except Exception as e:
            # 捕获轮询循环中的异常，避免程序崩溃
            logger.exception(f"轮询过程中发生异常: {e}")
            await asyncio.sleep(30)  # 发生异常时等待30秒后重试


async def process_creator(creator, queue, sem: asyncio.Semaphore):
    """处理单个创作者，获取视频列表并加入队列"""
    async with sem:
        try:
            videos = await creator.get_bilibili_videos()
            # 确保 videos 不为 None
            if videos is None:
                videos = []
            path = await creator.get_bilibili_path()
            record = RecordManager(path)
            # filter_videos 会自动清理残留的 downloading 状态
            videos = record.filter_videos(videos)
            creator_name = await creator.get_bilibili_name()
            if not videos:
                logger.info(f"未检测到新视频: {creator_name}")
            for vid in videos:
                event = DownloadEvent(vid_id=vid)
                await queue.put(event)
        except Exception as e:
            # 捕获所有异常，避免单个创作者的问题阻塞整个轮询
            logger.exception(f"处理创作者 {creator.uid} 时发生异常: {e}")


async def handle_download(event: DownloadEvent):
    """处理单个下载任务"""
    try:
        await VideoDown(vid_id=event.vid_id)
    except ErrorChargeVideo as e:
        logger.exception(e)
    except ResponseCodeException as e:
        logger.exception(f"{event.vid_id} 接口错误: {e.code}")


async def _run(event, queue, download_sem: asyncio.Semaphore):
    """运行下载任务并标记完成（受下载并发信号量限制）"""
    async with download_sem:
        try:
            await handle_download(event)
        finally:
            queue.task_done()


async def dispatcher(queue: asyncio.Queue, sem: asyncio.Semaphore):
    """分发下载任务"""
    while True:
        event = await queue.get()
        asyncio.create_task(_run(event, queue, sem))
