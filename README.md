# 微博超话(腾讯云函数版)
步骤：  
1.新建-自定义创建  
2.函数名称(随便取)-运行环境(python3.6)  
3.本地上传zip包(先把github下载的代码文件取出来再打包zip，直接复制粘贴过去也行╰(*°▽°*)╯)-执行方法 index.main  
[![fQLHLF.png](https://z3.ax1x.com/2021/08/08/fQLHLF.png)](https://imgtu.com/i/fQLHLF)  
4.点击完成  
5.函数管理-函数配置-编辑-环境变量  
[![fQxtN4.png](https://z3.ax1x.com/2021/08/08/fQxtN4.png)](https://imgtu.com/i/fQxtN4)  
[![fQx6ED.png](https://z3.ax1x.com/2021/08/08/fQx6ED.png)](https://imgtu.com/i/fQx6ED)  
  - 使用企业微信推送的需要添加上 AgentId、EnterpriseID、Secret、Touser(选填)  
  - Account、UserName 选填(只是为了区别账号而已...)  
  - sub 必填-浏览器登陆微博后在 cookie 里面找到 SUB=xxxx  
[![fQxQcq.png](https://z3.ax1x.com/2021/08/08/fQxQcq.png)](https://imgtu.com/i/fQxQcq)  
[![WcL1l8.png](https://z3.ax1x.com/2021/07/25/WcL1l8.png)](https://imgtu.com/i/WcL1l8)  
