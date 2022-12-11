import re
import logging

import requests

from apscheduler.schedulers.blocking import BlockingScheduler


logger = logging.getLogger()

formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

fileHandler = logging.FileHandler("FishC.log", encoding="utf-8", mode="a")
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

logger.setLevel(logging.DEBUG)


class FishC():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

    def login(self):
        signin_page_url = "https://fishc.com.cn/plugin.php?id=k_misign:sign"
        signin_page_req = self.session.get(signin_page_url)
        re_formhash = re.findall(r'<input type="hidden" name="formhash" value="(.*?)" />', signin_page_req.text)
        if re_formhash:
            formhash = re_formhash[0]
        else:
            logger.warning("Get login formhash failed.")
            self.login() # re login.

        login_url = "https://fishc.com.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
        data = {
            "username": self.username,
            "password": self.password,
            "formhash": formhash,
            "quickforward": "yes",
            "handlekey": "ls"
        }
        login_req = self.session.post(login_url, data=data) # login
        login_req = self.session.get(login_url) # get login info
        re_userinfo = re.findall(r"({'username.*?})", login_req.text)
        if "娆㈣繋鎮ㄥ洖鏉�" in login_req.text and re_userinfo:
            userinfo = eval(re_userinfo[0])
            logger.info("Login Success!")
            logger.info("uid -> {uid}".format(uid=userinfo["uid"]))
            logger.info("username -> {username}".format(username=userinfo["username"]))
            logger.info("usergroup -> {usergroup}".format(usergroup=userinfo["usergroup"]))
            return True
        else:
            logger.debug("Login Failed!")
            logger.debug("Reuqest Info")
            logger.debug("url -> {url}".format(url=login_url))
            logger.debug("data -> {data}".format(data=data))
            logger.debug("Response Info")
            logger.debug("Status Code -> {status_code}".format(status_code=login_req.status_code))
            logger.debug(login_req.text)
            return False



    def signin(self):
        signin_page_url = "https://fishc.com.cn/plugin.php?id=k_misign:sign"
        signin_page_req = self.session.get(signin_page_url)
        re_formhash = re.findall(r'<input type="hidden" name="formhash" value="(.*?)" />', signin_page_req.text)
        re_coin = re.findall('绉垎: (\d+)<', signin_page_req.text)
        if re_coin:
            coin = re_coin[0]
            logger.info("Coin -> {coin}".format(coin=coin))
        else:
            logger.warning("[-] Login failed, re login")
            login_status = self.login() # re login
            if login_status: # login success
                self.signin() # re sign
            else:
                logger.debug("Sign in , Login Failed!")
                return False
        if re_formhash:
            formhash = re_formhash[0]
        else:
            logger.warning("[-] Get sign in formhash failed.")
            self.signin() # re sign

        signin_url = "https://fishc.com.cn/plugin.php?id=k_misign:sign&operation=qiandao&formhash={formhash}&format=empty".format(formhash=formhash)

        signin_req = self.session.get(signin_url)
        logger.info("Sign in Success!")
        logger.debug("Sign in Info")
        logger.debug(signin_req.text)



def main():
    fishc = FishC("[USER]", "[PASS_MD5]")
    login_status = fishc.login() # login fisc
    if login_status:
        fishc.signin()
    else:
        return False

    sched = BlockingScheduler()
    sched.add_job(fishc.signin, "cron", hour=16) # every day 00:00 sign in.
    sched.start()

if __name__ == '__main__':
    main()
