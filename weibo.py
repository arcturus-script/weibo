from tools import handler
import requests as req
import re
import time
import random


CHAOHUA_URL = "https://api.weibo.cn/2/cardlist"

CHECKIN_URL = "https://api.weibo.cn/2/page/button"

TASK_URL = "https://m.weibo.cn/c/checkin/ug/v2/signin/signin"

# 获取用户信息
INFO = "https://api.weibo.cn/2/profile"


def parse_chaohua_item(card_group: list) -> list:
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

                print(f"[{super_item['id']}]: {super_item['title']}")

    return super_List


class Weibo:
    def __init__(self, **config) -> None:
        self.params = {
            "gsid": config.get("gsid"),  # 身份验证
            "c": "android",  # 客户端校验
            "from": config.get("from"),  # 客户端校验
            "s": config.get("s"),  # 校验参数
            "lang": "zh_CN",
            "networktype": "wifi",
            "uid": config.get("uid"),  # 用于获取用户信息
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

        print(" 开始获取超话列表 ".center(30, "#"))

        try:
            while True:
                params = {
                    "containerid": "100803_-_followsuper",
                    "fid": "100803_-_followsuper",
                    "since_id": since_id,
                    "cout": 20,
                }

                params.update(self.params)

                respJson = req.get(
                    CHAOHUA_URL,
                    headers=self.headers,
                    params=params,
                ).json()

                # 获得超话数组
                if "errno" not in respJson:
                    for card in respJson["cards"]:
                        # 将获得的 card_group 进行解析, 去掉不必要的内容
                        list_ = parse_chaohua_item(card["card_group"])
                        super_list.extend(list_)

                    # 获取下一页 id
                    since_id = respJson["cardlistInfo"]["since_id"]

                    # 获取到空就是爬取完了
                    if since_id == "":
                        print(f" 超话列表获取完毕({len(super_list)}) ".center(30, "#"))
                        break
                else:
                    raise Exception(respJson["errmsg"])
        except Exception as e:
            print(f"获取超话列表时出错, 原因: {e}")

        return super_list

    # 超话签到
    def chaohua_checkin(self, item: dict):
        try:
            if item["status"] == "签到":
                params = {
                    "request_url": f"http://i.huati.weibo.com/mobile/super/active_checkin?pageid={item['id']}&in_page=1"
                }

                params.update(self.params)

                respJson = req.get(
                    CHECKIN_URL,
                    headers=self.headers,
                    params=params,
                ).json()

                if "errno" in respJson:
                    raise Exception(respJson["errmsg"])
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

                    print(f"[success] {item['title']}")
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

                print(f"[success] {item['title']}")
        except Exception as e:
            msg = {
                "status": False,
                "msg": e,
                "title": item["title"],
                "exp": "",
                "score": "",
                "continute": "",
                "rank": "",
            }

        return msg

    # 获取用户信息
    def get_user_name(self):
        try:
            respJson = req.get(INFO, params=self.params, headers=self.headers).json()

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
            msg_list.append(msg)
            time.sleep(random.randint(10, 15))

        return {
            "name": self.name,
            "result": msg_list,
        }
