"""
登录相关功能
"""
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

