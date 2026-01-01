"""
cookies 的获取和持久化
"""

from bilibili_api import Credential
from bilicache.managers.config_manager import ConfigManager
from typing import Optional

_credential: Optional[Credential] = None


from bilibili_api import login_v2
import time


async def get_cookies():
    """获取B站登录cookies"""
    qr = login_v2.QrCodeLogin(platform=login_v2.QrCodeLoginChannel.WEB)
    await qr.generate_qrcode()
    print(qr.get_qrcode_terminal())
    while not qr.has_done():
        await qr.check_state()
        time.sleep(1)
    cookies = await qr.get_credential().get_buvid_cookies()

    return cookies


async def init_credential():
    """异步函数 需要 await"""
    global _credential
    config = ConfigManager()
    if not config.has("account", "cookies"):
        cookies = await get_cookies()
        config.set("account", "cookies", cookies)
    cookies = config.get("account", "cookies")
    _credential = Credential(
        sessdata=cookies["SESSDATA"],
        bili_jct=cookies["bili_jct"],
        buvid3=cookies["buvid3"],
        buvid4=cookies["buvid4"],
        dedeuserid=cookies["DedeUserID"],
        ac_time_value=cookies["ac_time_value"],
    )


def get_credential() -> Credential:
    if _credential is None:
        raise RuntimeError("未初始化credential,请在调用get()之前init()")
    return _credential
