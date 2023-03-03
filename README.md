# VeighNa框架的NasdaqData数据服务接口

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-2.10.14.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## 说明

基于Nasdaqdata的API开发，支持以下美国金融市场的免费K线数据：

* 加密货币：
  * Bitfinex：Bitfinex交易所
  


注意：需要注册获取数据服务权限，可以通过[该页面](https://data.nasdaq.com/sign-up)注册使用。


## 安装

安装环境推荐基于3.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

下载源代码后，解压后在cmd中运行：

```
pip install .
```


## 使用

在VeighNa中使用NasdaqData时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|datafeed.name|名称|是|nasdaqdata|
|datafeed.username|用户名|是|api_key|
|datafeed.password|密码|是|(请填写注册NasdaqData后，NasdaqData提供的api_key)|
