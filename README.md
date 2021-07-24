# 微博超话(腾讯云函数版)
步骤：  
1.新建-自定义创建  
2.函数名称(随便取)-运行环境(python3.6)  
3.本地上传zip包(先把github下载的代码文件取出来再打包zip，直接复制粘贴过去也行╰(*°▽°*)╯)-执行方法 index.main  
4.点击完成  
5.函数管理-函数配置-编辑-环境变量  
  - 使用企业微信推送的需要添加上 AgentId、EnterpriseID、Secret、Touser  
  - Touser、Account、UserName选填  
  - sub 必填-浏览器登陆微博后在cookie里面找到SUB=xxxx  
[![WcL1l8.png](https://z3.ax1x.com/2021/07/25/WcL1l8.png)](https://imgtu.com/i/WcL1l8)
sub小写！(╯°□°）╯︵ 
