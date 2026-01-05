import os
import asyncio
import logging
import logging.config
from .common.check import Check
from .config.cookies_locator import init_credential
from .config.ffmpeg_locator import init_ffmpeg
from .managers.config_manager import ConfigManager
from . import LOG_CONF
from .api.controller import poller, dispatcher


async def main() -> None:
    if not os.path.exists("./Download"):
        os.mkdir("./Download")
    Check.tempfile("./Download")
    init_credential()
    init_ffmpeg()
    config = ConfigManager()
    if config.get("logging", "debug"):
        LOG_CONF["loggers"]["bilicache"]["level"] = logging.DEBUG
        LOG_CONF["root"]["level"] = logging.DEBUG
    logging.config.dictConfig(LOG_CONF)

    queue = asyncio.Queue()
    download_sem = asyncio.Semaphore(config.get("download", "semaphore"))
    asyncio.create_task(poller(queue))
    asyncio.create_task(dispatcher(queue, download_sem))
    await asyncio.Event().wait()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
