from bilicache import Check
import unittest
class TestCheck(unittest.case):
    def test_ffmpeg():
        c=Check()
        c.check_ffmpeg()