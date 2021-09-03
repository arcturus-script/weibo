<div align="center">
<h1>微博超话(腾讯云函数版)</h1>

[![GitHub issues](https://img.shields.io/github/issues/ICE99125/weibo_checkin?style=for-the-badge)](https://github.com/ICE99125/weibo_checkin/issues) [![GitHub forks](https://img.shields.io/github/forks/ICE99125/weibo_checkin?style=for-the-badge)](https://github.com/ICE99125/weibo_checkin/network) [![GitHub stars](https://img.shields.io/github/stars/ICE99125/weibo_checkin?style=for-the-badge)](https://github.com/ICE99125/weibo_checkin/stargazers) [![Python](https://img.shields.io/badge/python-3.6%2B-orange?style=for-the-badge)](https://www.python.org/)
</div>

### 步骤
1.新建-自定义创建  
2.函数名称(随便取)  
3.本地上传zip包  
>🎄 先把 github 下载的代码文件取出来再打包成 zip  
>🎃 直接复制粘贴过去也行  

4.执行方法 index.main  
[![fQLHLF.png](https://z3.ax1x.com/2021/08/08/fQLHLF.png)](https://imgtu.com/i/fQLHLF)  
5.点击完成  
6.函数管理-函数配置-编辑-环境变量  
[![fQxtN4.png](https://z3.ax1x.com/2021/08/08/fQxtN4.png)](https://imgtu.com/i/fQxtN4)  
[![h64GPf.png](https://z3.ax1x.com/2021/09/03/h64GPf.png)](https://imgtu.com/i/h64GPf)   
7.超时时间设置成 900
### 环境变量
|key|描述|
|:----:|:----:|
|AgentId|应用id|
|EnterpriseID|企业id|
|Secret|应用密钥|
|Touser|不填默认全部成员|
|Account|(选填)只是为了区别账号而已|
|UserName|(选填)只是为了区别账号而已|
|sub|(必填)微博的cookie|
|push_type|推送服务类型|

📌 push_type
|值|描述|
| :----: | :----: |
|0|默认值(不使用推送)|
|1|企业微信|
|2|sever酱|

### 获取 sub  
经过查找发现 sina.cn 下的 sub 可以同时获取超话列表和签到   
[![hM3nQU.png](https://z3.ax1x.com/2021/08/27/hM3nQU.png)](https://imgtu.com/i/hM3nQU)  
[![hM3ezT.png](https://z3.ax1x.com/2021/08/27/hM3ezT.png)](https://imgtu.com/i/hM3ezT)
