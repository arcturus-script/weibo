import requests as req
import re
import time
import random


def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        table = [("超话", "排名", "经验", "积分", "连续天数", "结果")]
        for i in res["result"]:
            table.append(
                (
                    i["title"],
                    i["rank"],
                    i["exp"],
                    i["score"],
                    i["continute"],
                    i["msg"],
                )
            )

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
    CHAOHUA_URL = "https://api.weibo.cn/2/cardlist"
    CHECKIN_URL = "https://api.weibo.cn/2/page/button"
    TASK_URL = "https://m.weibo.cn/c/checkin/ug/v2/signin/signin"

    # 获取用户信息
    INFO = "https://api.weibo.cn/2/profile"

    def __init__(self, *, gsid, from_, s, uid) -> None:
        self.params = {
            "gsid": gsid,  # 身份验证
            "c": "android",  # 客户端校验
            "from": from_,  # 客户端校验
            "s": s,  # 校验参数
            "lang": "zh_CN",
            "networktype": "wifi",
            "uid": uid,  # 用于获取用户信息
        }
        self.headers = {
            "Host": "api.weibo.cn",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip",
            "content-type": "application/json;charset=utf-8",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)",
        }

        self.cookie = ""

    # 获取超话列表
    def get_chaohua_List(self) -> list:
        since_id = ""
        super_list = []

        print("开始获取超话列表".center(30, "#"))

        try:
            while True:
                params = {
                    "containerid": "100803_-_followsuper",
                    "fid": "100803_-_followsuper",
                    "since_id": since_id,
                    "cout": 20,  # 一次请求最多 20 个超话(不写好像也只能获取 20 个)
                }

                params.update(self.params)

                respJson = req.get(
                    Weibo.CHAOHUA_URL,
                    headers=self.headers,
                    params=params,
                ).json()

                # 获得超话数组
                if "errno" not in respJson:
                    for card in respJson["cards"]:
                        # 将获得的 card_group 进行解析, 去掉不必要的内容
                        list_ = Weibo.get_chaohua_item(card["card_group"])
                        super_list.extend(list_)

                    # 获取下一页 id
                    since_id = respJson["cardlistInfo"]["since_id"]

                    # 获取到空就是爬取完了
                    if since_id == "":
                        print("超话列表获取完毕".center(30, "#"))
                        break
                else:
                    raise Exception(respJson["errmsg"])
        except Exception as e:
            print(f"获取超话列表时出错, 原因: {e}")

        return super_list

    @staticmethod
    def get_chaohua_item(card_group: list) -> list:
        """[summary] 根据超话列表获取单个超话 id

        Args: card_group (list): 微博超话详细信息列表, 例如
            [{
                'card_type': '8',
                'itemid': 'follow_super_follow_1_0',
                'scheme': 'sinaweibo://pageinfo?containerid=100808b5abffe1359adcc70f8d6f38e60eea6e&extparam=%E7%B2%BE%E7%81%B5%E5%AE%9D%E5%8F%AF%E6%A2%A6%23tabbar_follow%3D4774056174031051',
                'title_sub': '精灵宝可梦',
                'pic': 'https://wx4.sinaimg.cn/thumbnail/c0448018gy1g07hid3wqmj20ro0rowk9.jpg',
                'pic_corner_radius': 6,
                'name_font_size': 15,
                'pic_size': 58,
                'buttons': [{
                    'type': 'link',
                    'pic': 'https://h5.sinaimg.cn/upload/100/582/2020/04/14/super_register_button_disable.png',
                    'name': '已签'
                }],
                'desc1': '等级 LV.8',
                'desc2': '#精灵宝可梦[超话]#lof那边让迷拟q回头的呼声太大所以追加了p2() \u200b',
                'openurl': '',
                'cleaned': True
            }, {...}]

        Returns: [list]: 精简后的超话信息, 例如
            [{
                "level": "LV.8",
                "title": "精灵宝可梦",
                "id": "100808b5abffe1359adcc70f8d6f38e60eea6e"
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
                    super_item = {
                        # 把 “等级 LV.9” 换成 “LV.9”
                        "level": re.findall(r"LV.\d", card["desc1"])[0],
                        "title": card["title_sub"],
                        "id": cid[0],
                        "status": card["buttons"][0]["name"],  # "已签" or "签到"
                    }
                    super_List.append(super_item)
                    print(f"[超话]: {super_item['title']}, id={super_item['id']}")

        return super_List

    # 超话签到
    def chaohua_checkin(self, item: dict):
        try:
            if item["status"] == "签到":
                print(f"🎉开始签到超话: {item['title']}")
                params = {
                    "request_url": f"http://i.huati.weibo.com/mobile/super/active_checkin?pageid={item['id']}&in_page=1"
                }

                params.update(self.params)

                respJson = req.get(
                    Weibo.CHECKIN_URL,
                    headers=self.headers,
                    params=params,
                ).json()

                if "errno" in respJson:
                    raise Exception(respJson["errmsg"])
                elif "error_msg" in respJson:
                    raise Exception(respJson["error_msg"])
                else:
                    msg = {
                        "status": True,
                        "msg": "签到成功",
                        "rank": respJson["fun_data"]["check_count"],  # 第几个签到
                        "score": respJson["fun_data"]["score"],  # 积分
                        "exp": respJson["fun_data"]["int_ins"],  # 经验
                        "continute": respJson["fun_data"]["check_int"],  # 连续签到
                        "title": item["title"],
                    }
            else:
                msg = {
                    "status": True,
                    "msg": "已签到",
                    "title": item["title"],
                    "exp": "",
                    "score": "",
                    "continute": "",
                    "rank": "",
                }
        except Exception as e:
            msg = {
                "status": False,
                "msg": e,
                "title": item["title"],
            }

        return msg

    # 任务中心签到(暂时不知道cookie怎么获取...)
    def task_checkin(self):
        try:
            headers = self.headers

            headers.update(
                {
                    "Host": "m.weibo.cn",
                    "Referer": f"https://m.weibo.cn/c/checkin?from={self.params['from']}&hash=sign",
                    "Cookie": self.cookie,
                }
            )

            respJson = req.get(
                Weibo.TASK_URL,
                headers=headers,
                params=self.params,
            ).json()

            print(respJson)

            if respJson["ok"] == 0:
                raise Exception(respJson["msg"])
            else:
                sign_in = respJson["data"]["sign_in"]

                if sign_in["show"] == 1:
                    continue_ = sign_in["continue"]  # 连续签到天数
                    value = sign_in["content"]["gift"]["points"]["value"]  # 签到积分

                    return {
                        "continue": continue_,
                        "value": value,
                    }
        except Exception as e:
            print(f"任务中心签到失败, 原因: {e}")

    # 获取用户信息
    def get_user_name(self):
        try:
            respJson = req.get(
                Weibo.INFO,
                params=self.params,
                headers=self.headers,
            ).json()

            if "errno" in respJson:
                raise Exception(respJson["errmsg"])
            else:
                self.name = respJson["userInfo"]["name"]
        except Exception as e:
            print(f"获取用户名时出错, 原因: {e}")
            self.name = "获取失败"

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
                time.sleep(random.randint(10, 15))
            else:
                break

        return {
            "name": self.name,
            "result": msg_list,
        }
