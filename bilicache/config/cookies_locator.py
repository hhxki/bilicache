"""
cookies 的获取和持久化
"""

from bilibili_api import Credential
from ..managers.config_manager import ConfigManager
from typing import Optional

_credential: Optional[Credential] = None


from bilibili_api import login_v2, Geetest, GeetestType
from bilibili_api.login_v2 import QrCodeLogin
import time


def get_qrcode_url(self):
    return self._QrCodeLogin__qr_link


QrCodeLogin.get_qrcode_url = get_qrcode_url


async def get_cookies_by_qrcode():
    import asyncio
    qr = login_v2.QrCodeLogin(platform=login_v2.QrCodeLoginChannel.WEB)
    await qr.generate_qrcode()
    import segno

    qr_segno = segno.make(qr.get_qrcode_url())
    print(qr_segno.terminal(compact=True))
    while not qr.has_done():
        await qr.check_state()
        await asyncio.sleep(1)  # 使用异步睡眠而不是同步 sleep
    cookies = await qr.get_credential().get_buvid_cookies()
    return cookies


async def get_cookies_by_pwd():
    import asyncio
    import sys
    
    gee = Geetest()  # 实例化极验测试类
    await gee.generate_test()  # 生成测试
    gee.start_geetest_server()  # 在本地部署网页端测试服务
    print(gee.get_geetest_server_url())  # 获取本地服务链接
    while not gee.has_done():  # 如果测试未完成
        await asyncio.sleep(0.1)  # 使用异步睡眠而不是忙等待
    gee.close_geetest_server()  # 关闭部署的网页端测试服务
    print("result:", gee.get_result())

    # 在异步环境中安全地获取输入
    if sys.version_info >= (3, 9):
        username = await asyncio.to_thread(input, "username:")  # 手机号/邮箱
        password = await asyncio.to_thread(input, "password:")  # 密码
    else:
        loop = asyncio.get_running_loop()
        username = await loop.run_in_executor(None, lambda: input("username:"))
        password = await loop.run_in_executor(None, lambda: input("password:"))
    
    cred = await login_v2.login_with_password(
        username=username, password=password, geetest=gee  # 调用接口登录
    )

    # 安全验证
    if isinstance(cred, login_v2.LoginCheck):
        # 如法炮制 Geetest
        gee = Geetest()  # 实例化极验测试类
        await gee.generate_test(
            type_=GeetestType.VERIFY
        )  # 生成测试 (注意 type_ 为 GeetestType.VERIFY)
        gee.start_geetest_server()  # 在本地部署网页端测试服务
        print(gee.get_geetest_server_url())  # 获取本地服务链接
        while not gee.has_done():  # 如果测试未完成
            await asyncio.sleep(0.1)  # 使用异步睡眠而不是忙等待
        gee.close_geetest_server()  # 关闭部署的网页端测试服务
        print("result:", gee.get_result())
        await cred.send_sms(gee)  # 发送验证码
        if sys.version_info >= (3, 9):
            code = await asyncio.to_thread(input, "code:")
        else:
            loop = asyncio.get_running_loop()
            code = await loop.run_in_executor(None, lambda: input("code:"))
        cred = await cred.complete_check(code)  # 调用接口登录
    return cred.get_cookies()


async def get_cookies_by_sms():
    import asyncio
    import sys
    
    gee = Geetest()  # 实例化极验测试类
    await gee.generate_test()  # 生成测试
    gee.start_geetest_server()  # 在本地部署网页端测试服务
    print(gee.get_geetest_server_url())  # 获取本地服务链接
    while not gee.has_done():  # 如果测试未完成
        await asyncio.sleep(0.1)  # 使用异步睡眠而不是忙等待
    gee.close_geetest_server()  # 关闭部署的网页端测试服务
    print("result:", gee.get_result())
    
    # 在异步环境中安全地获取输入
    if sys.version_info >= (3, 9):
        phone_str = await asyncio.to_thread(input, "phone:")
    else:
        loop = asyncio.get_running_loop()
        phone_str = await loop.run_in_executor(None, lambda: input("phone:"))
    phone = login_v2.PhoneNumber(phone_str, "+86")  # 实例化手机号类
    captcha_id = await login_v2.send_sms(phonenumber=phone, geetest=gee)  # 发送验证码
    print("captcha_id:", captcha_id)  # 顺便获得对应的 captcha_id
    
    if sys.version_info >= (3, 9):
        code = await asyncio.to_thread(input, "code: ")
    else:
        loop = asyncio.get_running_loop()
        code = await loop.run_in_executor(None, lambda: input("code: "))
    
    cred = await login_v2.login_with_sms(
        phonenumber=phone, code=code, captcha_id=captcha_id  # 调用接口登录
    )
    # 安全验证
    if isinstance(cred, login_v2.LoginCheck):
        # 如法炮制 Geetest
        gee = Geetest()  # 实例化极验测试类
        await gee.generate_test(
            type_=GeetestType.VERIFY
        )  # 生成测试 (注意 type_ 为 GeetestType.VERIFY)
        gee.start_geetest_server()  # 在本地部署网页端测试服务
        print(gee.get_geetest_server_url())  # 获取本地服务链接
        while not gee.has_done():  # 如果测试未完成
            await asyncio.sleep(0.1)  # 使用异步睡眠而不是忙等待
        gee.close_geetest_server()  # 关闭部署的网页端测试服务
        print("result:", gee.get_result())
        await cred.send_sms(gee)  # 发送验证码
        if sys.version_info >= (3, 9):
            code = await asyncio.to_thread(input, "code:")
        else:
            loop = asyncio.get_running_loop()
            code = await loop.run_in_executor(None, lambda: input("code:"))
        cred = await cred.complete_check(code)  # 调用接口登录

    return cred.get_cookies()  # 获得 cookies


async def get_cookies():
    """获取B站登录cookies"""
    import asyncio
    import sys
    
    print(
        f"""
    ================= 登录方式 =================
    [1].二维码登录
    [2].账号密码登录
    [3].短信验证码登录
    ===========================================
    请输入对应的数字回车...
    """
    )
    # 在异步环境中，使用 asyncio.to_thread 或直接在线程中执行 input
    # 对于 Python 3.9+，使用 asyncio.to_thread
    if sys.version_info >= (3, 9):
        choose = await asyncio.to_thread(input)
    else:
        # 对于旧版本 Python，使用 run_in_executor
        loop = asyncio.get_running_loop()
        choose = await loop.run_in_executor(None, input)
    
    choose = choose.strip()
    if choose == "1":
        cookies = await get_cookies_by_qrcode()
    elif choose == "2":
        cookies = await get_cookies_by_pwd()
    elif choose == "3":
        cookies = await get_cookies_by_sms()
    else:
        raise InterruptedError("输入其他选项")

    config = ConfigManager()
    config.set("account", "cookies", cookies)
    return cookies


def init_credential():
    """初始化credential"""
    global _credential
    config = ConfigManager()
    if not config.has("account", "cookies"):
        return

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
    return _credential
