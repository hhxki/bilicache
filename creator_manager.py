from bilibili_api.user import User
from bilibili_api import ResponseCodeException
import os
import asyncio
from config_manager import ConfigManager


class CreatorManager:
    def __init__(self, uid):
        self.uid = str(uid)
        self.config = ConfigManager("./config/creator.toml")

    @staticmethod
    def get_bilibili_creator_list():
        config = ConfigManager("./config/creator.toml")
        uid_list = config.get_key("bilibili")
        creators = []
        for uid in uid_list:
            creators.append(CreatorManager(uid))
        return creators

    async def get_bilibili_videos(self):
        try:
            up = User(self.uid)
            info = await up.get_overview_stat()
            total = info["video"]
            page_size = 30
            page = 1
            bvids = []
            while len(bvids) < total:
                videos = await up.get_videos(ps=page_size, pn=page)
                vlist = videos["list"]["vlist"]
                if not vlist:
                    break
                bvids.extend(v["bvid"] for v in vlist)
                page += 1
                await asyncio.sleep(0.3)
            return bvids
        except ResponseCodeException as e:
            if e.code == -404:
                self.log_out_creator()

    async def get_bilibili_name(self):
        try:
            creator_info = self.config.get("bilibili", self.uid)
            if not creator_info:
                up = User(self.uid)
                info = await up.get_user_info()
                creator_info = dict()
                creator_info["name"] = info["name"]
                self.config.set("bilibili", self.uid, creator_info)
            return creator_info["name"]
        except ResponseCodeException as e:
            if e.code == -404:
                creator_info = dict()
                creator_info["name"] = "用户已注销"
                self.config.set("bilibili", self.uid, creator_info)
            return creator_info["name"]

    async def get_bilibili_path(self):
        name = await self.get_bilibili_name()
        path = f"./Download/{name}"
        if not os.path.exists(path):
            os.mkdir(path)
        return f"{path}/"
