import os
import asyncio
import logging
import logging.config
from bilicache import (
    ConfigManager,
    poller,
    dispatcher,
    Check,
    init_credential,
    LOG_CONF,
)


async def main() -> None:
    if not os.path.exists("./Download"):
        os.mkdir("./Download")
    Check.tempfile("./Download")
    init_credential()
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


if __name__ == "__main__":
    asyncio.run(main())
