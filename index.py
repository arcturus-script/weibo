import requests
import time
import push
import re
import os
''' 是否使用推送？
    0: 不使用
    1: 企业微信
    2: 待定
'''
push_type = '1'


# 获取超话列表
def get_chaohua_List(Cookie):
    # 获取超话列表的API
    url = 'https://weibo.com/ajax/profile/topicContent?tabid=231093_-_chaohua'
    headers = {
        'Cookie':
        Cookie,
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67',
        'Referer':
        'https://weibo.com/u/page/follow/5251799448/231093_-_chaohua',
        'sec-ch-ua':
        '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"'
    }
    respJson = requests.get(url, headers=headers).json()
    chaohua_list = get_chaohua_item(respJson['data']['list'])
    return chaohua_list


# 根据超话列表获取单个超话id
def get_chaohua_item(list_):
    super_list = list()
    for item in list_:
        chaohua_item = {'id': item['oid'][5:], 'title': item['title']}
        super_list.append(chaohua_item)
    return super_list


# 超话签到
def chaohua_checkin(Cookie, item):
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67'
    time_now = int(round(time.time() * 1000))
    data = {
        'ajwvr': 6,
        'api': 'http://i.huati.weibo.com/aj/super/checkin',
        'id': item['id'],
        'location': 'page_%s_super_index' % item['id'][0:6],
        'timezone': 'GMT 0800',
        'lang': 'zh-cn',
        'plat': 'Win32',
        'ua': ua,
        'screen': '1280*720',
        '__rnd': time_now
    }
    # 超话签到地址
    url = 'https://weibo.com/p/aj/general/button'
    headers = {
        'cookie':
        Cookie,
        'user-Agent':
        ua,
        'Referer':
        'https://weibo.com/p/' + item['id'] + '/super_index',
        'sec-ch-ua':
        '"Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"'
    }
    response = requests.get(url, headers=headers, params=data)
    respJson = response.json()

    if 'code' in respJson:
        if respJson['code'] == '100000':
            msg = ('话题[%s]签到成功-第%s个签到-获得%s经验' %
                   (item['title'],
                    re.findall(r'\d+', respJson['data']['alert_title'])[0],
                    re.findall(r'\d+', respJson['data']['alert_subtitle'])[0]))
            print(msg)
            return msg
        elif respJson['code'] == 382004:
            msg = ('话题[%s]-今日已签到' % item['title'])
            print(msg)
            return msg
    else:
        print('签到失败')
        return {'title': item['title'], 'error': '签到失败'}


def start():
    Cookie = 'SUB=' + os.environ['sub']
    # 获取超话列表
    chaohua_list = get_chaohua_List(Cookie)
    print(chaohua_list)
    msg_list = []
    for item in chaohua_list:
        msg = chaohua_checkin(Cookie, item)
        msg_list.append(msg)
        time.sleep(15)
    if push_type == '1':
        # 使用企业微信推送
        content = '\n'.join(msg_list)
        # 企业微信消息推送所需参数
        AgentId = os.environ['AgentId']  # 应用ID
        Secret = os.environ['Secret']  # 应用密钥
        EnterpriseID = os.environ['EnterpriseID']  # 企业ID
        Touser = os.getenv('Touser', '')  # 用户ID
        # 其他
        UserName = os.getenv('UserName','')
        Account = os.getenv('Account', '')
        # 进行推送
        p = push.qiye_wechat(AgentId, Secret, EnterpriseID, Touser)
        p.push_text_message('微博超话', content)
    else:
        # 暂时不写
        pass

def main(event,context):
    return start()

if __name__ == '__main__':
    start()
