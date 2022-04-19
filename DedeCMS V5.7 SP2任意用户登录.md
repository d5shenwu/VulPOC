# DedeCMS V5.7 SP2任意用户登录

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

织梦内容管理系统(Dedecms)是一款PHP开源网站管理系统。dedecms 的会员模块的身份认证使用的是客户端 session，在 Cookie 中写入用户 ID 并且附上 `ID__ckMd5`，用做签名。主页存在逻辑漏洞，导致可以返回指定 uid 的 ID 的 Md5 散列值，可以伪造任意用户登录，并可以因此修改管理员密码。

## 漏洞影响

DedeCMS V5.7 SP2

## 漏洞复现

首先需要有一个用户，注册一个即可，但是注册的用户名不能随便，对应了想要登录用户的 `id` ，然后需要管理员审核通过，不然没法访问空间，无法进行攻击

比如这里，我注册的用户名是 `0000001` ，对应的是 `admin` 的 `id` ，登陆后访问链接并抓包

```plain
http://www.dedecms521.com/member/index.php?uid=0000001
```

这里需要注意，要把  `cookie` 中的带 `last_` 的部分删掉，不然不会生成新的 `cookie` ，参数 `uid` 对应的是这个用户名

![img](https://gitee.com/N0puple/nopic/raw/master/img/20210704180301.png)

将 `cookie` 中的 `DedeUserID` 设置为这里得到的 `cookie` 中的 `last_vid` ，`DedeUserID__ckMd5` 设置为这里得到的 `cookie` 中的 `last_vid`，再访问链接，即可发现成功访问到了另外的用户，这里是 `admin`

```plain
http://www.dedecms521.com/member/index.php
```

![img](https://gitee.com/N0puple/nopic/raw/master/img/image-20210704180648323.png)

## 总结

这个漏洞的主要是伪造 `cookie` ，这里的 `cookie` 存在验证，可以利用另外会被设置成 `cookie` 的值来伪造，最后使用到 `intval` ，由于用户名最少需要 3 位，所以伪造的时候只能伪造成 `0001` 等形式，巧妙使用 `intval` 来还原了这个数值，虽然只能伪造到 `member` 表中的 `admin` ，但是结合之前的漏洞可以实现进入后台（存在一定限制，需要管理员关闭注册详细信息）。

## 参考链接

-  https://wiki.bylibrary.cn/漏洞库/01-CMS漏洞/DedeCMS/Dedecms任意用户登录SSV-97087/ 

-  https://www.seebug.org/vuldb/ssvid-97087 



`github` 链接：`https://github.com/N0puple/vulPOC`

获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”
