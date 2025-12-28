from bilibili_api.user import User
import os
import asyncio
from config_manager import ConfigManager


class CreatorManager:
    def __init__(self, uid):
        self.uid = str(uid)

    async def get_bilibili_videos(self):
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

    async def get_bilibili_name(self):
        config = ConfigManager("./config/creator.toml")
        creator_info = config.get("bilibili", self.uid)
        if creator_info == {} or creator_info == None:
            up = User(self.uid)
            info = await up.get_user_info()
            creator_info = dict()
            creator_info["name"] = info["name"]
            config.set("bilibili", self.uid, creator_info)
        return creator_info["name"]

    async def get_bilibili_path(self):
        name = await self.get_bilibili_name()
        path = f"./Download/{name}"
        if not os.path.exists(path):
            os.mkdir(path)
        return f"{path}/"
