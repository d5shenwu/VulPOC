# XunRuiCMS 前台RCE漏洞

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

先后在两篇文章中看到了这个`cms`，利用方式感觉很有意思，遂跟着复现一波写下了这篇文章。

## 漏洞影响

影响在此修复之前的版本 

https://gitee.com/dayrui/xunruicms/commit/80e2d8f3008384d926c64163b7334a260edc0a51

此处测试环境为修复的前一个版本，可 `git` 下载后执行命令

```
git checkout fad7b01
```

## 漏洞复现

实际上是这个洞分为两部分，一部分是变量覆盖，另一部分是文件包含。这里通过变量覆盖可以控制写入 `html` 文件的内容，最后通过文件包含导致了命令执行。

因为调用 `display`的地方使用了 `ob_start`，因此一般的命令都没有回显，所以使用的弹计算器的方式

自己弹了一下自己，只是我的计算器早就被我删了（注：下面的 `www.xunruicms.com` 是我本地的命名，与其他地方无关 ）

```php
python3 xunrui_cms_unauth_RCE.py http://www.xunruicms.com calc.exe
```

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1644334744634-94e79d78-cf97-4ec2-a5a3-d576a8405421.png)

## 总结

利用方式很有意思，但是有一点点复杂，有兴趣的话可以自己手调一下，会有更多的收获的，若是有什么疑问的地方，欢迎私聊交流讨论。

## 参考链接

- [https://xz.aliyun.com/t/10002](https://xz.aliyun.com/t/10002)
- https://forum.butian.net/share/1072



`github` 链接：`https://github.com/N0puple/vulPOC`

