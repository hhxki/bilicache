from bilibili_api.user import User
import asyncio
class CreatorManager():
    def __init__(self,uid):
        self.uid=uid

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
            asyncio.sleep(0.3)
        return bvids


