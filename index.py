from urllib.parse import urlparse
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
    since_id = ''
    super_list = list()
    num = 0
    while True:
        # 获取超话列表的API
        url = 'https://m.weibo.cn/api/container/getIndex?containerid=100803_-_followsuper&since_id=' + since_id
        headers = {
            'Cookie':
            Cookie,
            'User-Agent':
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer':
            'https://m.weibo.cn/p/tabbar?containerid=100803_-_recentvisit&page_type=tabbar'
        }
        respJson = requests.get(url, headers=headers).json()
        num += 1
        # 开始解析
        # 获得超话数组
        if respJson['ok'] == 1:
            cards = respJson['data']['cards'][0]
            card_group = cards['card_group']
            # 将获得的 card_group 进行解析 去掉不必要的内容
            list_ = get_chaohua_item(card_group)
            super_list.extend(list_)
            # 获取下一页id
            since_id = respJson['data']['cardlistInfo']['since_id']
            # 获取到空就是爬取完了
            if since_id == '':
                break
        else:
            print('超话列表为空')
            break
    return super_list


# 根据超话列表获取单个超话id
def get_chaohua_item(card_group):
    super_List = []
    for card in card_group:
        # card['card_type'] == '8' 是超话
        # card['card_type'] == '42' 是“我的关注”
        if card['card_type'] == '8':
            # 获得超话链接
            scheme = card['scheme']
            # 对超话链接进行解析获得参数列表
            query = urlparse(scheme).query
            parmsList = query.split('&')
            containerid = ''
            # 获得超话的 containerid
            for parm in parmsList:
                r = parm.split('=')
                if r[0] == 'containerid':
                    containerid = r[1]
                    break
            super_item = {
                'level':
                re.sub(u'([^\u0041-\u005a\u0061-\u007a\u0030-\u0039])', '',
                       card['desc1']),
                'title': card['title_sub'],
                'id': containerid
            }
            super_List.append(super_item)
    return super_List


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
    print(respJson)

    if 'code' in respJson:
        if respJson['code'] == '100000' or respJson['code'] == 100000:
            msg = ('话题[%s]签到成功-第%s个签到-获得%s经验' %
                   (item['title'],
                    re.findall(r'\d+', respJson['data']['alert_title'])[0],
                    re.findall(r'\d+', respJson['data']['alert_subtitle'])[0]))
            print(msg)
            return msg
        elif respJson['code'] == 382004 or respJson['code'] == '382004':
            msg = ('话题[%s]-今日已签到' % item['title'])
            print(msg)
            return msg
        else:
            return ('话题[%s]-签到失败' % item['title'])
    else:
        return ('话题[%s]-签到失败' % item['title'])


def start():
    Cookie1 = 'SUB=' + os.environ['sub1']
    Cookie2 = 'SUB=' + os.environ['sub2']
    # 获取超话列表
    chaohua_list = get_chaohua_List(Cookie1)
    print(chaohua_list)
    msg_list = []
    for item in chaohua_list:
        msg = chaohua_checkin(Cookie2, item)
        msg_list.append(msg)
        time.sleep(15)
    if push_type == '1':
        # 使用企业微信推送
        content = '\n'.join('%s' % l for l in msg_list)
        # 企业微信消息推送所需参数
        AgentId = os.environ['AgentId']  # 应用ID
        Secret = os.environ['Secret']  # 应用密钥
        EnterpriseID = os.environ['EnterpriseID']  # 企业ID
        Touser = os.getenv('Touser', '@all')  # 用户ID
        # 其他
        UserName = os.getenv('UserName', '')
        Account = os.getenv('Account', '')
        # 进行推送
        p = push.qiye_wechat(AgentId, Secret, EnterpriseID, Touser)
        p.push_text_message('微博超话', content, UserName, Account)
    else:
        # 暂时不写
        pass

def main(event,context):
    return start()
