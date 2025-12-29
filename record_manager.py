from config_manager import ConfigManager


class RecordManager:
    def __init__(self, path):
        self.path = f"{path}.record.toml"
        self.config = ConfigManager(self.path)

    def has(self, bvid):
        records = self.config.get("download", "record") or {}
        return bvid in records

    def add(self, bvid, title):
        if self.has(bvid):
            return
        records = self.config.get("download", "record") or {}
        records[bvid] = title
        self.config.set("download", "record", records)
