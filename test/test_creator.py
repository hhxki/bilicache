import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(".."))
from creator_manager import CreatorManager
from pprint import pprint


class testCreatorManager(unittest.TestCase):
    def test_get_bili_video(self):
        async def run():
            creator = CreatorManager(3546912688966277)
            res = await creator.get_bilibili_videos()
            pprint(res)
        asyncio.run(run())
    def test_get_bili_name(self):
        async def run():
            creator = CreatorManager(3546912688966277)
            res=await creator.get_bilibili_name()
            print(res)
        asyncio.run(run())
    def test_get_list_name(self):
        res=CreatorManager.get_list_bilibili_creator()
        pprint(res)

if __name__ == "__main__":
    unittest.main()
