import sys
import os
import asyncio
import logging
import logging.config
from bilicache import ConfigManager, poller, dispatcher, Check, init_credential

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
    if not os.path.exists("./Download"):
        os.mkdir("./Download")
    Check.tempfile("./Download")
    await init_credential()
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
