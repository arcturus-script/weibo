# 微博超话(腾讯云函数版)
步骤：  
1.新建-自定义创建  
2.函数名称(随便取)-运行环境(python3.6)  
3.本地上传zip包(先把github下载的代码文件取出来再打包zip)-执行方法 index.main  
4.点击完成  
5.函数管理-函数配置-编辑-环境变量  
  - 使用企业微信推送的需要添加上AgentId、EnterpriseID、Secret、Touser  
  - Account、UserName选填  
  - sub必填-浏览器登陆微博后在cookie里面找到SUB=xxxx  
