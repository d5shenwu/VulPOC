# CatfishCMS文件上传漏洞（CNVD-2021-42363）

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述
逛 `cnvd` 的时候看到 `catfish cms` 的文件上传漏洞，于是审了审，就发现了这两处文件上传，具体是不是该漏洞，还有待考证。

### CNVD编号

CNVD-2021-42363

### 影响范围

文中标的是 `Catfish CMS V5.9.6` ，但这里这个我看了下，最新能下载到的 `v5.9.12` 也受到影响

## 漏洞复现

有两个漏洞，不过都需要登陆后台，而且类型都差不多，不过利用方式可以有些区别

#### 上传主题 getshell

```
后台 -> 系统设置 -> 主题 -> 主题上传
```

我们去看看主题的位置

```
CatfishCMS-5.9.6\public
```

可以看到这里已经有了几个主题，再加上明确有说是上传 `zip`，因此随便复制一个文件夹出来，将我们的马写进去，然后打包成 `zip` 上传就可以 `getshell`

```
http://www.xxxxx.com/public/blogs/bat.php
```

#### 上传插件 getshell

这个和之前那个几乎是一模一样的

```
扩展功能 -> 插件 -> 插件上传
```

插件位置

```
CatfishCMS-5.9.6\application\plugins
```

这里有一个 `announcement` ，复制出来，在里面加一个马，打包 `zip` 上传，插件处不一定显示，有可能是因为内容都一样的原因，不过确实传上去了，但是我们想要像主题一样直接 `getshell` 是不行的，访问

```
http://www.xxxxxxxxxxx.com/application/plugins/annn/shell.php
```

![](https://img-blog.csdnimg.cn/img_convert/07275e6ad90e2cc68f1446e52344aa0f.png)

我们发现是无法直接访问的，究其原因，原来是 `.htaccess` 在作怪，`.htaccess` ，分布式配置文件，可以针对目录改变配置，我们可以在 `application` 文件夹下面发现他，看看里面的内容

```
deny from all
```

也就是 `application` 文件夹，包括其子目录拒绝一切访问，这才想起来，他是一个 `thinkphp` 程序，不让直接访问 `application` 就是正常的操作，想想怎么绕过这个限制呢，在子文件夹中的 `.htaccess`  优先级是更高的，因此我们同时上传一个 `.htaccess` ，内容

```
allow from all
```

这样就可以直接访问到了，至此， `getshell` 成功

## 总结

这里我并没有分析其漏洞代码，造成漏洞的主要原因是允许压缩包内的任意文件上传，这也是开发人员常常忽略的点，只注意上传的文件，而没有在意之后解压出来的文件，从而导致了漏洞，此外 `.htaccess` 这一手确实挺有意思的，作用很大，当然，其实也可以 `user.ini`  



## 参考链接

- https://www.cnvd.org.cn/flaw/show/CNVD-2021-42363

`github` 链接：`https://github.com/N0puple/vulPOC`

