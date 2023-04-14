def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        table = [("超话", "排名", "经验", "积分", "连续天数", "结果")]

        for i in res["result"]:
            el = (i["title"], i["rank"], i["exp"], i["score"], i["continute"], i["msg"])

            table.append(el)

        return [
            {
                "h4": {
                    "content": f"用户名: {res['name']}",
                },
                "table": {
                    "contents": table,
                },
            }
        ]

    return inner
