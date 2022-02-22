import requests as req
import time
import json
import re


def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        table = [("超话", "第几个签到", "经验", "签到结果")]
        for i in res["result"]:
            table.append((i["title"], i["rank"], i["experience"], i["msg"]))

        return [
            {
                "h4": {
                    "content": f"用户名: {res['name']}",
                },
                "table": {
                    "content": table,
                },
            }
        ]

    return inner


class Weibo:
    CHAOHUA_URL = "https://m.weibo.cn/api/container/getIndex"
    CHECKIN_URL = "https://weibo.com/p/aj/general/button"

    # 获取用户信息
    GROUP = "https://weibo.com/ajax/feed/allGroups"
    INFO = "https://weibo.com/ajax/profile/info"

    def __init__(self, sub) -> None:
        self.cookie = f"SUB={sub}"
        self.headers = {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Referer": "https://m.weibo.cn/p/tabbar?containerid=100803_-_recentvisit&page_type=tabbar",
        }

    # 获取超话列表
    def get_chaohua_List(self) -> list:
        since_id = ""
        super_list = []

        print("开始获取超话列表".center(30, "#"))
        while True:
            try:
                playload = {
                    "containerid": "100803_-_followsuper",
                    "since_id": since_id,
                }
                respJson = req.get(
                    Weibo.CHAOHUA_URL,
                    headers=self.headers,
                    params=playload,
                ).json()

                # 获得超话数组
                if respJson["ok"] == 1:
                    for card in respJson["data"]["cards"]:
                        # 将获得的 card_group 进行解析, 去掉不必要的内容
                        list_ = Weibo.get_chaohua_item(card["card_group"])
                        super_list.extend(list_)

                    # 获取下一页 id
                    since_id = respJson["data"]["cardlistInfo"]["since_id"]

                    # 获取到空就是爬取完了
                    if since_id == "":
                        print("超话列表获取完毕".center(30, "#"))
                        break
                else:
                    print("超话列表为空".center(30, "#"))
                    break
            except json.JSONDecodeError:
                print("sub 不对哦 😥 获取不到超话列表")
                break
        return super_list

    # 根据超话列表获取单个超话 id
    @staticmethod
    def get_chaohua_item(card_group: list) -> list:
        """[summary]

        Args:
            card_group (list): 微博超话详细信息列表, 例如 [{
                "card_type": "8",
                "itemid": "follow_super_follow_1_9",
                "scheme": "https://m.weibo.cn/p/index?containerid=1008088233e594e02a4d7a23ef5c28c19cb031&extparam=%E5%BB%BA%E7%AD%91%E9%92%A2%E7%AC%94%E7%94%BB%23tabbar_follow%3D4730360640833176&luicode=10000011&lfid=100803_-_followsuper",
                "title_sub": "建筑钢笔画",
                "pic": "https://ww4.sinaimg.cn/thumb180/41f8c78bjw1farmhj8scoj20e80a2tak.jpg",
                "pic_corner_radius": 6,
                "buttons": [
                    {
                        "type": "link",
                        "pic": "https://h5.sinaimg.cn/upload/100/582/2020/04/14/super_register_button_disable_default.png",
                        "name": "已签",
                        "scheme": False,
                    }
                ],
                "desc1": "等级 LV.9",
                "desc2": "#建筑钢笔画[超话]# \u200b",
            }, {...}]

        Returns:
            [list]: 精简后的超话信息, 例如 [{
                "level": "LV.9",
                "title": "建筑钢笔画",
                "id": "1008088233e594e02a4d7a23ef5c28c19cb031"
            }, { ... }]
        """
        super_List = []
        for card in card_group:
            if card["card_type"] == "8":

                # 获得超话链接
                scheme = card["scheme"]
                # 获得超话的 containerid
                cid = re.findall(
                    "(?<=containerid=).*?(?=&)|(?<=containerid=).*",
                    scheme,
                )
                if len(cid) > 0:
                    containerid = cid[0]
                    super_item = {
                        # 把 “等级 LV.9” 换成 “LV.9”
                        "level": re.findall(r"LV.\d", card["desc1"])[0],
                        "title": card["title_sub"],
                        "id": containerid,
                    }
                    super_List.append(super_item)
                    print(f"[超话]: {super_item['title']}, id={super_item['id']}")
        return super_List

    # 超话签到
    def chaohua_checkin(self, item: dict):
        playload = {
            "ajwvr": 6,
            "api": "http://i.huati.weibo.com/aj/super/checkin",
            "id": item["id"],
            "location": f"page_{item['id'][0:6]}_super_index",
            "timezone": "GMT 0800",
            "lang": "zh-cn",
            "plat": "Win32",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
            "screen": "1280*720",
            "__rnd": int(round(time.time() * 1000)),
        }
        headers = {
            "cookie": self.cookie,
            "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
            "Referer": f"https://weibo.com/p/{item['id']}/super_index",
            "sec-ch-ua": '"Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
        }
        try:
            print(f"🐼 开始签到超话[{item['title']}]...")
            respJson = req.get(
                Weibo.CHECKIN_URL,
                headers=headers,
                params=playload,
            ).json()

            if "code" in respJson:
                code = int(respJson["code"])
                if code == 100000:
                    rank = respJson["data"]["alert_title"]
                    exp = respJson["data"]["alert_subtitle"]

                    msg = {
                        "status": True,
                        "msg": "签到成功",
                        "title": item["title"],
                        "rank": re.findall(r"\d+", rank)[0],  # 第几个签到
                        "experience": re.findall(r"\d+", exp)[0],  # 经验
                    }

                    print(
                        f"🌟 话题[{item['title']}]签到成功, 第{msg['rank']}个签到, 获得{ msg['experience']}点经验"
                    )

                    return msg
                elif code == 382004:
                    msg = {
                        "status": True,
                        "msg": "今日已签到",
                        "title": item["title"],
                        "rank": "N/A",
                        "experience": 0,
                    }

                    print(f"🍪 话题[{item['title']}]今日已签到")

                    return msg
                elif code == 382006:
                    print(f"🤡 权限错误, 请尝试使用 sina.cn 下的 sub 重试")
                    return {"status": False}
                elif code == 402003:
                    print(f"😭 系统繁忙, 请稍后重试")
                    return {"status": False}
                elif code == 100003:
                    print(f"😡 最近行为异常")
                    return {"status": False}
            else:
                print(f"😭 签到失败, 未知原因")
                return {"status": False}
        except Exception as exp:
            print(f"😭 签到时出现错误, 原因: {exp}")
            return {"status": False}

    @handler
    def start(self):
        # 获取用户名
        self.get_user_name()

        # 获取超话列表
        chaohua_list = self.get_chaohua_List()

        msg_list = []
        for item in chaohua_list:
            msg = self.chaohua_checkin(item)
            if msg["status"]:
                msg_list.append(msg)
                time.sleep(1)
            else:
                break

        return {
            "name": self.name,
            "result": msg_list,
        }

    # 获取用户信息
    def get_user_name(self):
        try:
            headers = {"cookie": self.cookie}
            res = req.get(Weibo.GROUP, headers=headers).json()

            uid = ""

            for i in res["groups"]:
                for j in i["group"]:
                    uid = j["uid"]
                    break

            print(f"获取到用户的 uid: {uid}")

            params = {"uid": uid}
            res = req.get(Weibo.INFO, params=params, headers=headers).json()

            if res["ok"] == 1:
                name = res["data"]["user"]["screen_name"]
            else:
                name = "无"

            self.name = name
            print(f"获取到用户名: {name}")

        except Exception as ex:
            print(f"获取用户名时出错, 原因: {ex}")
            self.name = "无"
