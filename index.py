from urllib.parse import urlparse
import requests
import time
import json
import push
import re
import os


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
        try:
            respJson = requests.get(url, headers=headers).json()
            num += 1
            # 开始解析
            # 获得超话数组
            if respJson['ok'] == 1:
                for i in range(len(respJson['data']['cards'])):
                    cards = respJson['data']['cards'][i]
                    card_group = cards['card_group']
                    # 将获得的 card_group 进行解析 去掉不必要的内容
                    list_ = get_chaohua_item(card_group)
                    super_list.extend(list_)
                # 获取下一页 id
                since_id = respJson['data']['cardlistInfo']['since_id']
                # 获取到空就是爬取完了
                if since_id == '':
                    break
            else:
                print('超话列表为空')
                break
        except json.JSONDecodeError:
            print('sub 不对哦 😥 获取不到超话列表')
            break
    return super_list


# 根据超话列表获取单个超话 id
def get_chaohua_item(card_group):
    super_List = []
    for card in card_group:
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
                'title':
                card['title_sub'],
                'id':
                containerid
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
        if int(respJson['code']) == 100000:
            msg = {
                'title':
                item['title'],
                'rank':
                re.findall(r'\d+', respJson['data']['alert_title'])[0],
                'experience':
                re.findall(r'\d+', respJson['data']['alert_subtitle'])[0],
                'result':
                '签到成功'
            }

            message = ('话题[%s]签到成功-第%s个签到-获得%s经验' %
                       (msg['title'], msg['rank'], msg['experience']))
            print(message)
            return msg
        elif int(respJson['code']) == 382004:
            msg = {
                'title': item['title'],
                'rank': '',
                'experience': '',
                'result': '今日已签到'
            }
            message = ('话题[%s]-%s' % (msg['title'], msg['result']))
            print(message)
            return msg
        else:
            msg = {
                'title': item['title'],
                'rank': '',
                'experience': '',
                'result': '签到失败'
            }
            return msg
    else:
        msg = {
            'title': item['title'],
            'rank': '',
            'experience': '',
            'result': '签到失败'
        }
        return msg


def start():
    subList = os.environ['sub'].split(',')
    msg_list = list()
    for subItem in subList:
        Cookie = 'SUB=' + subItem
        # 获取超话列表
        chaohua_list = get_chaohua_List(Cookie)
        print(chaohua_list)
        msg_list_item = []
        for item in chaohua_list:
            msg = chaohua_checkin(Cookie, item)
            msg_list_item.append(msg)
            time.sleep(1)
        msg_list.append(msg_list_item)

    push_type = os.getenv('push_type', 0)
    # 账号和昵称
    UserName = os.getenv('UserName', '').split(',')
    Account = os.getenv('Account', '').split(',')
    if push_type == '1':
        # 企业微信消息推送所需参数
        AgentId = os.environ['AgentId']  # 应用ID
        Secret = os.environ['Secret']  # 应用密钥
        EnterpriseID = os.environ['EnterpriseID']  # 企业ID
        Touser = os.getenv('Touser', '@all')  # 用户ID

        for index, msg_list_item in enumerate(msg_list):
            msg = []
            for item in msg_list_item:
                if '失败' or '已签到' in item['result']:
                    message = ('话题[%s]-%s' % (item['title'], item['result']))
                    msg.append(message)
                else:
                    message = (
                        '话题[%s]签到成功-第%s个签到-获得%s经验' %
                        (item['title'], item['rank'], item['experience']))
                    msg.append(message)
            content = '\n'.join(msg)

            # 进行推送
            p = push.qiye_wechat(AgentId, Secret, EnterpriseID, Touser)
            try:
                p.push_text_message('微博超话', content, UserName[index], Account[index])
            except IndexError:
                p.push_text_message('微博超话', content)

    elif os.getenv('Key', '') and push_type != '0':
        content = ''
        for index, msg_list_item in enumerate(msg_list):
            try:
                Account_ = ('### 账号：' + Account[index])
                UserName_ = ('### 用户名：' + UserName[index])
            except IndexError:
                Account_ = ''
                UserName_ = ''
            content = content + Account_ + UserName_ + (
                '|超话|经验|第几个签到|签到结果|\n'
                '|:----:|:----:|:----:|:----:|\n')

            for item in msg_list_item:
                msg = '|' + item['title'] + '|' + item[
                    'experience'] + '|' + item['rank'] + '|' + item[
                        'result'] + '|\n'
                content = content + msg

        key = os.environ['Key']
        if push_type == '2':
            # 使用 sever 酱推送
            p = push.server(key)
        elif push_type == '3':
            # 使用 pushplus 酱推送
            p = push.pushplus(key)

        p.push_message('微博超话', content)


def main(event, context):
    return start()


if __name__ == '__main__':
    start()
