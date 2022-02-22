config = {
    "multi": [
        {
            "sub": "账号1",
            "push": "pushplus", # together 为 True 时失效, 不写不推送
        },
        # {
        #     "sub": "账号2",
        #     "push": "pushplus",
        # },
    ],
    "together": True, # 是否合并发送结果, 不写或 True 时合并发送
    "push": "pushplus", # 推送类型, together 为 True 或者不写时必须有, 否则不推送
}
