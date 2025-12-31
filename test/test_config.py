import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(".."))
from bilicache import ConfigManager


class TestConfigManager(unittest.TestCase):
    def test_creat_config(self):
        config = ConfigManager("./config/creator.toml")
        self.assertIsInstance(config, ConfigManager, msg="类初始化失败")

    def test_save_config(self):
        config = ConfigManager("creator.toml")
        config.set("bilibili", "3546912688966277", {})

    def test_save_record_config(self):
        config = ConfigManager("record.toml")
        config.set(
            "download",
            "record",
            {"bvsdaihsd": "first", "bvsdahiu": "second"},
        )
        config.set(
            "download",
            "record",
            {"bvsdaihsd": "first", "bvsdahiu": "second", "bvsaoidh": "third"},
        )

    def test_get_config(self):
        config = ConfigManager("creator.toml")
        self.test_save_config()
        value = config.get("bilibili", "3546912688966277")
        self.assertEqual(value, {})

    def test_get_none_config(self):
        config = ConfigManager("creator.toml")
        res = config.get("asdddfs", "asdasd")
        self.assertEqual(res, None, msg="返回不存在的结果")

    def test_has_config(self):
        config = ConfigManager("creator.toml")
        self.assertTrue(config.has("bilibili", "3546912688966277"))
        self.assertTrue(config.has("bilibili"))
        self.assertFalse(config.has("sad"))


if __name__ == "__main__":
    unittest.main()
