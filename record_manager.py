from config_manager import ConfigManager
import os
import logging


class RecordManager:
    def __init__(self, path):
        self.path = f"{path}.record.toml"
        self.download_path = path
        self.config = ConfigManager(self.path)

    def has(self, bvid):
        """检查视频是否已下载完成"""
        records = self.config.get("download", "record") or {}
        return bvid in records

    def is_downloading(self, bvid, title=None):
        """检查视频是否正在下载（通过状态或临时文件）"""
        # 检查 downloading 状态
        downloading = self.config.get("download", "downloading") or {}
        if bvid in downloading:
            return True
        
        # 检查临时文件是否存在
        if title:
            temp_video = f"{self.download_path}{title}_temp.mp4"
            temp_audio = f"{self.download_path}{title}_temp.m4a"
            if os.path.exists(temp_video) or os.path.exists(temp_audio):
                return True
        
        return False

    def mark_downloading(self, bvid, title):
        """原子性地标记视频为下载中（如果尚未标记）"""
        # 使用 ConfigManager 的内部锁来保证原子性
        with self.config._lock:
            # 重新加载最新数据（防止读取到过期数据，不获取锁因为已持有）
            self.config._load(require_lock=False)
            downloading = self.config.get("download", "downloading") or {}
            # 如果已经在 downloading 中，返回 False 表示标记失败
            if bvid in downloading:
                return False
            downloading[bvid] = title
            # 在锁保护下更新并保存
            self.config.data.setdefault("download", {})
            self.config.data["download"]["downloading"] = downloading
            self.config._save(require_lock=False)
        return True

    def unmark_downloading(self, bvid):
        """取消下载中标记（不立即保存，用于批量更新）"""
        downloading = self.config.get("download", "downloading") or {}
        if bvid in downloading:
            del downloading[bvid]
            self.config.data.setdefault("download", {})
            self.config.data["download"]["downloading"] = downloading
    
    def unmark_downloading_and_save(self, bvid):
        """取消下载中标记并立即保存"""
        self.unmark_downloading(bvid)
        self.config._save()

    def add(self, bvid, title):
        """添加下载完成记录"""
        # 在锁保护下进行，保证原子性
        with self.config._lock:
            self.config._load(require_lock=False)  # 重新加载最新数据，不获取锁
            # 无论是否已存在，都先清理 downloading 状态（防止残留）
            downloading = self.config.get("download", "downloading") or {}
            if bvid in downloading:
                del downloading[bvid]
                self.config.data.setdefault("download", {})
                self.config.data["download"]["downloading"] = downloading
            
            # 检查是否已存在
            records = self.config.get("download", "record") or {}
            if bvid in records:
                # 即使已存在，也要保存（因为可能清理了 downloading 状态）
                self.config._save(require_lock=False)
                return
            
            # 添加到完成记录
            records[bvid] = title
            self.config.data.setdefault("download", {})
            self.config.data["download"]["record"] = records
            self.config._save(require_lock=False)  # 一次性保存所有更改

    def cleanup_stale_downloading(self):
        """清理残留的 downloading 状态（如果临时文件不存在且视频未完成）"""
        # 在锁保护下进行，保证原子性
        with self.config._lock:
            self.config._load(require_lock=False)  # 重新加载最新数据，不获取锁
            downloading = self.config.get("download", "downloading") or {}
            records = self.config.get("download", "record") or {}
            cleaned = []
            
            for bvid, title in list(downloading.items()):
                # 如果已经在完成记录中，清理 downloading 状态
                if bvid in records:
                    cleaned.append(bvid)
                    continue
                
                # 检查临时文件是否存在
                temp_video = f"{self.download_path}{title}_temp.mp4"
                temp_audio = f"{self.download_path}{title}_temp.m4a"
                # 如果临时文件都不存在，说明下载已中断或完成，清理状态
                if not os.path.exists(temp_video) and not os.path.exists(temp_audio):
                    cleaned.append(bvid)
            
            # 批量清理找到的残留状态（只更新一次文件）
            if cleaned:
                for bvid in cleaned:
                    if bvid in downloading:
                        del downloading[bvid]
                self.config.data.setdefault("download", {})
                self.config.data["download"]["downloading"] = downloading
                self.config._save(require_lock=False)  # 只保存一次
                logger = logging.getLogger("bilicache")
                logger.info(f"清理了 {len(cleaned)} 个残留的 downloading 状态: {cleaned}")
        
        return len(cleaned)

    def filter_videos(self, videos):
        """过滤掉已下载和正在下载的视频"""
        # 先清理残留的 downloading 状态
        self.cleanup_stale_downloading()
        
        records = set(self.config.get("download", "record") or {})
        downloading = set(self.config.get("download", "downloading") or {})
        
        # 排除已下载和正在下载的视频
        videos = [vid for vid in videos if vid not in records and vid not in downloading]
        return videos
