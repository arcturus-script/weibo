import requests as req
import re
import time
import random


# 过滤不必要的信息
def filter(card_group):
    _list = []

    for card in card_group:
        if card["card_type"] == "8":
            # container_id
            cid = re.findall(
                "(?<=containerid=).*?(?=&)|(?<=containerid=).*",
                card["scheme"],
            )

            if len(cid) > 0:
                super_item = {
                    "level": re.findall(r"LV.\d", card["desc1"])[0],
                    "title": card["title_sub"],
                    "id": cid[0],
                    "status": card["buttons"][0]["name"],
                }

                _list.append(super_item)

    return _list


class userInfo:
    def __init__(self):
        self.uid = ""
        self.name = ""
        self.location = ""
        self.description = ""
        self.cover_image = ""


class weibo:
    def __init__(self, conf):
        self.info = userInfo()
        self.info.uid = conf["uid"]

        self.params = {
            "gsid": conf["gsid"],  # 身份验证
            "c": "android",  # 客户端校验
            "from": conf["from"],  # 客户端校验
            "s": conf["s"],  # 校验参数
            "uid": conf["uid"],  # 用于获取用户信息
        }

        self.headers = {
            "Host": "api.weibo.cn",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip",
            "content-type": "application/json;charset=utf-8",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)",
            "Authorization": f"WB-SUT {conf['gsid']}",
        }

    # 获取超话列表
    def get_chaohua_List(self) -> list:
        since_id = ""
        _list = []

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
                    "https://api.weibo.cn/2/cardlist",
                    headers=self.headers,
                    params=params,
                ).json()

                # 获得超话数组
                if "errno" not in respJson:
                    for card in respJson["cards"]:
                        li = filter(card["card_group"])
                        _list.extend(li)

                    # 获取下一页 id
                    since_id = respJson["cardlistInfo"]["since_id"]

                    # 获取到空就是爬取完了
                    if since_id == "":
                        print("超话列表获取完毕")
                        for i in _list:
                            print(f"{i['title']}: {i['id']}")
                        break
                else:
                    raise Exception(respJson["errmsg"])
        except Exception as e:
            print(f"获取超话列表时出错, 原因: {e}")

        return _list

    # 超话签到
    def chaohua_checkin(self, item: dict):
        try:
            if item["status"] == "签到":
                params = {
                    "request_url": f"http://i.huati.weibo.com/mobile/super/active_checkin?pageid={item['id']}&&sg_tab_config=2&in_page=1"
                }

                params.update(self.params)

                respJson = req.get(
                    "https://api.weibo.cn/2/page/button",
                    headers=self.headers,
                    params=params,
                ).json()

                if "errno" in respJson:
                    raise Exception(respJson["errmsg"])
                else:
                    print(f"[success] {item['title']}")

                    return {
                        "status": True,
                        "msg": "签到成功",
                        "rank": respJson["fun_data"]["check_count"],  # 第几个签到
                        "score": respJson["fun_data"]["score"],  # 积分
                        "exp": respJson["fun_data"]["int_ins"],  # 经验
                        "continute": respJson["fun_data"]["check_int"],  # 连续签到
                        "title": item["title"],
                    }
            else:
                print(f"[success] {item['title']}")

                return {
                    "status": False,
                    "msg": "已签到",
                    "title": item["title"],
                }

        except Exception as e:
            return {
                "status": False,
                "msg": e,
                "title": item["title"],
            }

    # 获取用户信息
    def update_user_info(self):
        url = "https://api.weibo.cn/2/profile"
        respJson = req.get(url, params=self.params, headers=self.headers).json()
        user_info = respJson["userInfo"]

        self.info.name = user_info["name"]
        self.info.location = user_info["location"]
        self.info.description = user_info["description"]
        self.info.cover_image = user_info["cover_image"]

    def start(self):
        self.update_user_info()

        # 获取超话列表
        chaohua_list = self.get_chaohua_List()

        messages = []
        for item in chaohua_list:
            time.sleep(random.randint(5, 10))
            res = self.chaohua_checkin(item)
            messages.append(res)

        table = [("超话", "排名", "经验", "积分", "连续天数", "结果")]

        for msg in messages:
            if msg["status"]:
                el = (
                    msg["title"],
                    msg["rank"],
                    msg["exp"],
                    msg["score"],
                    msg["continute"],
                    msg["msg"],
                )
            else:
                el = (msg["title"], "", "", "", "", msg["msg"])

            table.append(el)

        return {
            "title": "微博超话签到",
            "message": [
                {
                    "txt": {"content": f"用户名: {self.info.name}", "end": "\n\n"},
                    "table": {"contents": table, "end": "\n\n"},
                }
            ],
        }
