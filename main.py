import sys
import os
import asyncio
import logging
import logging.config
from bilibili_api import Credential, ResponseCodeException

from bilicache import ConfigManager, get_cookies, poller, dispatcher

LOG_CONF = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(filename)s[line:%(lineno)d](Pid:%(process)d "
            "Tname:%(threadName)s) %(levelname)s %(message)s",
            # 'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(filename)s%(lineno)d[%(levelname)s]Tname:%(threadName)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": logging.DEBUG,
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "simple",
        },
        "file": {
            "level": logging.DEBUG,
            "class": "bilicache.common.log.SafeRotatingFileHandler",
            "when": "W0",
            "interval": 1,
            "backupCount": 1,
            "filename": "ds_update.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": logging.INFO,
    },
    "loggers": {
        "bilicache": {
            "handlers": ["file"],
            "level": logging.INFO,
        },
    },
}


async def main() -> None:
    logging.config.dictConfig(LOG_CONF)
    logger = logging.getLogger("bilicache")
    if not os.path.exists("./Download"):
        os.mkdir("./Download")
    config = ConfigManager()
    if not config.has("account", "cookies"):
        cookies = await get_cookies()
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
    queue = asyncio.Queue()
    sem = asyncio.Semaphore(5)
    asyncio.create_task(poller(queue, credential))
    asyncio.create_task(dispatcher(queue, sem))
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
