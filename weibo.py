import requests as req
import re, time, random


class Weibo:
    def __init__(self, cookie):
        self.session = req.Session()
        self.user_info = {}
        self.session.cookies.update(cookie)
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "upgrade-insecure-requests": "1",
                "sec-ch-ua": '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "navigate",
                "sec-fetch-dest": "document",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "priority": "u=0, i",
            }
        )

    def update_cookie(self):
        resp = self.session.get("https://weibo.com")
        self.user_info["uid"] = resp.headers["x-log-uid"]
        self.session.headers.update(
            {
                "x-xsrf-token": self.session.cookies["XSRF-TOKEN"],
            }
        )

    def get_chaohua_list(self):
        res = []

        headers = dict(self.session.headers)
        headers.update(
            {
                "referer": f"https://weibo.com/u/page/follow/{self.user_info['uid']}/231093_-_chaohua",
            }
        )

        def get_one_page(page):
            max_page = 0
            params = {"tabid": "231093_-_chaohua", "page": page}

            resp = self.session.get("https://weibo.com/ajax/profile/topicContent", params=params, headers=headers).json()
            result = []

            if "ok" in resp and resp["ok"] == 1:
                max_page = resp["data"]["max_page"]
                chaohua = resp["data"]["list"]
                for li in chaohua:
                    result.append({"title": li["title"], "id": li["oid"].split(":")[1]})

            return result, max_page

        try:
            result, max_page = get_one_page(1)
            res.extend(result)

            for p in range(2, max_page + 1):
                result, _ = get_one_page(p)
                res.extend(result)
        except Exception as e:
            print(f"获取超话列表时出错, 原因: {e}")

        return res

    def chaohua_checkin(self, id, title):
        print(f"正在签到超话: {title} ...")

        try:
            url = "https://weibo.com/p/aj/general/button"

            headers = dict(self.session.headers)
            headers.update(
                {
                    "referer": f"https://weibo.com/p/{id}/super_index",
                }
            )

            params = {
                "ajwvr": "6",
                "api": "http://i.huati.weibo.com/aj/super/checkin",
                "texta": "签到",
                "textb": "已签到",
                "status": "0",
                "id": id,
                "location": "page_100808_super_index",
                "timezone": "GMT+0800",
                "lang": "zh-cn",
                "plat": "Win32",
                "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
                "screen": "2560*1440",
                "__rnd": str(int(time.time() * 1000)),
            }

            resp = self.session.get(url, params=params).json()

            if "code" in resp:
                if str(resp["code"]) == "100000":
                    print(f"签到结果: {resp['data']['tipMessage']}")

                    return {
                        "title": title,
                        "message": resp["data"]["tipMessage"],
                        "experience": str(re.search(r"\d+", resp["data"]["tipMessage"]).group(0)),  # type: ignore
                        "rank": str(re.search(r"\d+", resp["data"]["alert_title"]).group(0)),  # type: ignore
                    }
                elif str(resp["code"]) == "382004":
                    print(f"签到结果: {resp['msg']}")

                    return {
                        "title": title,
                        "message": resp["msg"],
                        "experience": "",
                        "rank": "",
                    }

        except Exception as e:
            print(f"超话签到失败, 原因: {e}")
            return {
                "title": title,
                "message": "签到失败",
                "experience": "",
                "rank": "",
            }

    def update_user_info(self):
        headers = dict(self.session.headers)
        headers.update(
            {
                "referer": f"https://weibo.com/u/{self.user_info['uid']}",
            }
        )
        resp = self.session.get(f"https://weibo.com/ajax/profile/info?uid={self.user_info['uid']}", headers=headers).json()

        if "ok" in resp and resp["ok"] == 1:
            user = resp["data"]["user"]
            self.user_info.update(
                {
                    "name": user["screen_name"],
                    "location": user["location"],
                    "description": user["description"],
                }
            )

    def start(self):
        self.update_cookie()
        self.update_user_info()
        chaohua_list = self.get_chaohua_list()

        messages = []
        for item in chaohua_list:
            time.sleep(random.randint(1, 3))
            res = self.chaohua_checkin(item["id"], item["title"])
            messages.append(res)
