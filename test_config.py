import unittest
from config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def test_creat_config(self):
        config = ConfigManager()
        self.assertIsInstance(config, ConfigManager, msg="类初始化失败")

    def test_save_config(self):
        config = ConfigManager()
        config.set("setting", "问候", ["你好", "hello"])

    def test_get_config(self):
        config = ConfigManager()
        self.test_save_config()
        hello=config.get("setting","问候")
        self.assertEqual(hello, ["你好", "hello"])

    def test_change_config(self):
        config=ConfigManager()
        config.set("change","1to2",1)
        self.assertEqual(1, config.get("change", "1to2"))
        config.set("change","1to2",2)
        self.assertEqual(2, config.get("change", "1to2"))

    def test_get_none_config(self):
        config=ConfigManager()
        res=config.get("asdddfs","asdasd")
        self.assertEqual(res,None,msg="返回不存在的结果")

    def test_has_config(self):
        config=ConfigManager()
        self.assertTrue(config.has("setting", "问候"))
        self.assertTrue(config.has("setting"))
        self.assertFalse(config.has("sad"))


if __name__ == "__main__":
    unittest.main()
