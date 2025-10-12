from weibo import Weibo
from configs import configs

if __name__ == "__main__":
    for config in configs:
        w = Weibo(config)
        w.start()
