import unittest
from creator_manager import CreatorManager
from pprint import pprint
class testAuthorManager(unittest.TestCase):
    def test_get_bili_video(self):
        creator = CreatorManager(3546912688966277)
        pprint(creator.get_bilibili_videos())

if __name__=="main":
    unittest.main()
