from weibo import weibo
from config import config
from push_tools import push_creator
from dict2str import dict2str


def parse_message(message, msg_type):
    print(dict2str(message, type=msg_type))
    return str(dict2str(message, type=msg_type))


def push_message(message, push_config):
    if isinstance(push_config, list):

        for item in push_config:
            t = item.get("type")
            p = push_creator(t, item.get("key"))
            m = item.get("msgtype") or item.get("template", "markdown")

            item.pop("type")
            item.pop("key")

            msg = parse_message(message, m)
            p.send(msg, title=message["title"], **item)
    else:
        t = push_config.get("type")
        p = push_creator(t, push_config.get("key"))
        m = push_config.get("msgtype") or push_config.get("template", "markdown")

        push_config.pop("type")
        push_config.pop("key")

        msg = parse_message(message["message"], m)
        p.send(msg, title=message["title"], **push_config)


def main(*_):
    configs = config.get("multi")
    push_together = config.get("push")

    messages = []

    for conf in configs:
        obj = weibo(conf)

        res = obj.start()

        push = conf.get("push")

        if push is None:
            if push_together is not None:
                messages.append(res)
        else:
            push_message(res, push)

    if len(messages) != 0 and push_together is not None:
        m = []
        for msg in messages:
            m.extend(msg["message"])

        msg = {"title": messages[0]["title"], "message": m}
        push_message(msg, push_together)


if __name__ == "__main__":
    main()
