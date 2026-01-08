"""
创作者管理器
"""
from bilibili_api.user import User
from bilibili_api import ResponseCodeException
import os
import asyncio
import logging

from .config_manager import ConfigManager

logger = logging.getLogger("bilicache")


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
                # 用户不存在或已注销，返回空列表
                return []
            # 其他错误码也返回空列表，避免阻塞
            logger.warning(f"获取用户 {self.uid} 视频列表失败: {e.code}")
            return []
        except Exception as e:
            # 捕获所有其他异常，避免阻塞
            logger.exception(f"获取用户 {self.uid} 视频列表时发生异常")
            return []

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
            # 其他错误码，尝试使用配置中的名称或返回默认值
            logger.warning(f"获取用户 {self.uid} 信息失败: {e.code}")
            try:
                creator_info = self.config.get("bilibili", self.uid)
                if creator_info and "name" in creator_info:
                    return creator_info["name"]
            except:
                pass
            return f"用户{self.uid}"
        except Exception as e:
            # 捕获所有其他异常
            logger.exception(f"获取用户 {self.uid} 名称时发生异常")
            try:
                creator_info = self.config.get("bilibili", self.uid)
                if creator_info and "name" in creator_info:
                    return creator_info["name"]
            except:
                pass
            return f"用户{self.uid}"

    async def get_bilibili_path(self):
        name = await self.get_bilibili_name()
        path = f"./Download/{name}"
        if not os.path.exists(path):
            os.mkdir(path)
        return f"{path}/"

