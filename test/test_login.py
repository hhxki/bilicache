import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(".."))
from bilicache.config.cookies_locator import get_cookies,init_credential
import asyncio

class testLogin(unittest.TestCase):
    def test_init_cookies(self):
        self.assertIsNone(init_credential())
        async def run():
            await get_cookies()
        asyncio.run(run())

if __name__ == "__main__":
    unittest.main()
