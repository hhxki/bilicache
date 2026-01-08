import aiohttp
from pathlib import Path
import os
import shutil
import platform
from urllib.parse import urlparse
from ..managers.config_manager import ConfigManager
import logging
import socket

logger = logging.getLogger("bilicache")


class Check:
    def __init__(self):
        pass

    @staticmethod
    def ffmpeg() -> str:
        """
        查找 ffmpeg 可执行文件路径
        优先级：
        1. 环境变量 PATH
        2. 配置文件中的 ffmpeg 路径
        3. 提示用户安装 ffmpeg
        """
        config = ConfigManager()
        system = platform.system().lower()
        ffmpeg_name = "ffmpeg.exe" if system == "windows" else "ffmpeg"
        if config.get("ffmpeg", "use_env"):
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                logger.debug(f"[ffmpeg] 使用环境变量: {ffmpeg_path}")
                return ffmpeg_path

        try:
            cfg_path = config.get("ffmpeg", "path")
        except Exception:
            cfg_path = None

        if cfg_path:
            cfg_path = os.path.expanduser(cfg_path)

            if os.path.isfile(cfg_path):
                logger.debug(f"[ffmpeg] 使用固定路径: {cfg_path}")
                return cfg_path

            candidate = os.path.join(cfg_path, ffmpeg_name)
            if os.path.isfile(candidate):
                logger.debug(f"[ffmpeg] 使用固定路径: {candidate}")
                return candidate
        raise FileNotFoundError(
            "未找到 ffmpeg：\n"
            "1. 环境变量 PATH 中不存在 ffmpeg\n"
            "2. 配置文件中未正确指定 ffmpeg 路径\n\n"
            "请安装 ffmpeg 并确保：\n"
            "- Windows: https://ffmpeg.org/download.html\n"
            "- Linux: sudo apt install ffmpeg / sudo yum install ffmpeg"
        )

    @staticmethod
    async def network(timeout=5, retries=2):
        """
        检查网络连接（强制使用IPv4）
        
        Args:
            timeout: 单次请求超时时间（秒）
            retries: 重试次数
        
        Returns:
            bool: 网络是否可用
        """
        import asyncio
        
        # 多个检测目标（优先使用IP地址，避免DNS解析问题）
        check_targets = [
            # 使用 IP 地址，避免 DNS 解析问题
            ("http://14.215.177.39", "百度IP"),
            ("http://220.181.38.148", "百度IP备用"),
            # 如果IP访问失败，尝试域名（会强制IPv4解析）
            ("http://www.baidu.com", "百度域名"),
            ("http://www.qq.com", "腾讯"),
        ]
        
        # 强制使用 IPv4 的 DNS 解析函数
        async def resolve_host_ipv4(hostname: str) -> str:
            """强制使用 IPv4 解析域名"""
            try:
                # 使用 getaddrinfo 强制只获取 IPv4 地址（在线程池中执行）
                loop = asyncio.get_event_loop()
                addrinfo = await loop.run_in_executor(
                    None,
                    socket.getaddrinfo,
                    hostname,
                    None,
                    socket.AF_INET,  # 只使用 IPv4
                    socket.SOCK_STREAM
                )
                if addrinfo:
                    # 返回第一个 IPv4 地址
                    return addrinfo[0][4][0]
                return None
            except Exception as e:
                logger.debug(f"DNS解析 {hostname} 失败: {e}")
                return None
        
        # 尝试每个目标，直到成功
        for target_url, target_name in check_targets:
            for attempt in range(retries):
                try:
                    # 解析 URL 中的主机名
                    parsed = urlparse(target_url)
                    hostname = parsed.hostname
                    
                    # 检查是否是有效的 IPv4 地址
                    def is_ipv4_address(hostname: str) -> bool:
                        """检查字符串是否是有效的 IPv4 地址"""
                        try:
                            parts = hostname.split('.')
                            if len(parts) != 4:
                                return False
                            for part in parts:
                                if not part.isdigit():
                                    return False
                                num = int(part)
                                if num < 0 or num > 255:
                                    return False
                            return True
                        except:
                            return False
                    
                    # 如果主机名是 IP 地址，直接使用
                    if is_ipv4_address(hostname):
                        ip_address = hostname
                        logger.debug(f"使用直接IP地址: {ip_address}")
                    else:
                        # 强制使用 IPv4 解析域名
                        ip_address = await resolve_host_ipv4(hostname)
                        if not ip_address:
                            logger.debug(f"无法解析 {hostname} 的IPv4地址，跳过")
                            break  # 尝试下一个目标
                        logger.debug(f"解析 {hostname} -> {ip_address}")
                    
                    # 使用解析得到的 IP 地址构建 URL
                    if parsed.port:
                        check_url = f"{parsed.scheme}://{ip_address}:{parsed.port}{parsed.path}"
                    else:
                        check_url = f"{parsed.scheme}://{ip_address}{parsed.path}"
                    
                    # 创建强制使用 IPv4 的连接器
                    connector = aiohttp.TCPConnector(
                        family=socket.AF_INET,  # 强制 IPv4
                        ssl=False,
                        force_close=True,  # 强制关闭连接，避免连接池问题
                        enable_cleanup_closed=True
                    )
                    
                    try:
                        # 设置超时
                        timeout_config = aiohttp.ClientTimeout(
                            total=timeout,
                            connect=timeout,
                            sock_read=timeout
                        )
                        
                        # 创建会话并发送请求
                        async with aiohttp.ClientSession(
                            connector=connector,
                            timeout=timeout_config,
                            headers={"User-Agent": "Mozilla/5.0 (compatible; bilicache/1.0)"}
                        ) as session:
                            async with session.get(
                                check_url,
                                allow_redirects=True
                            ) as resp:
                                status = resp.status
                                if status == 200:
                                    logger.debug(f"网络检测成功: {target_name} ({check_url})")
                                    return True
                                else:
                                    logger.debug(f"网络检测失败: {target_name} 返回状态码 {status}")
                    finally:
                        # 确保连接器被正确关闭
                        await connector.close()
                    
                except socket.gaierror as e:
                    # DNS 解析错误
                    logger.debug(f"DNS解析错误 ({target_name}): {e}")
                    break  # 尝试下一个目标
                except asyncio.TimeoutError:
                    logger.debug(f"连接超时 ({target_name}, 尝试 {attempt + 1}/{retries})")
                    if attempt < retries - 1:
                        await asyncio.sleep(0.5)  # 重试前等待
                    continue
                except aiohttp.ClientError as e:
                    logger.debug(f"HTTP客户端错误 ({target_name}): {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(0.5)
                    continue
                except Exception as e:
                    logger.debug(f"网络检测异常 ({target_name}): {type(e).__name__}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(0.5)
                    continue
        
        # 所有目标都失败了
        logger.debug("所有网络检测目标均失败")
        return False

    @staticmethod
    def tempfile(root_dir: str):
        """清理临时文件：
        - *_temp.*
        - 0 字节文件（通常是下载中断或占位失败）
        """
        root = Path(root_dir)
        if not root.exists():
            raise FileNotFoundError(f"目录不存在: {root}")

        for file in root.rglob("*"):
            if not file.is_file():
                continue

            try:
                is_temp = "_temp" in file.stem
                is_zero = file.stat().st_size == 0

                if is_temp or is_zero:
                    file.unlink()
                    logger.debug(f"已删除临时文件: {file}")

            except Exception as e:
                logger.warning(f"删除失败: {file} | {e}")

    @staticmethod
    def safe_filename(filename: str) -> str:
        """将文件名中的非法字符替换为下划线"""
        return (
            filename.replace("\\", "_")
            .replace("/", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace('"', "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )

    @staticmethod
    def acquire_filename(path: str, title: str, suffix=".mp4") -> str:
        """并发安全的文件名获取（原子级）"""
        index = 0
        while True:
            name = title if index == 0 else f"{title}({index})"
            full = os.path.join(path, name + suffix)
            try:
                fd = os.open(full, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return name
            except FileExistsError:
                index += 1
