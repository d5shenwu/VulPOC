# WeiPHP5.0 前台任意文件上传漏洞

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

`WeiPHP5.0`是在2019年停止更新的一个系统，漏洞挺多的，跟着复现分析一下，这里复现一下 `WeiPHP5.0`的前台任意文件上传漏洞

## 漏洞影响

`WeiPHP5.0`最新版

可以据此下载

https://www.weiphp.cn/doc/download_source_installation.html

## 漏洞复现

存在一个 `upload_root` 方法是可以前台访问的，因为只使用了 `php` 黑名单过滤，因此存在多种绕过方式

### 法一：错误配置

有些系统默认可以解析 `phtml `, `php5` 等文件，可以利用该方法绕过

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1644771779522-6b3b4f27-3ff5-498c-9fd4-212bf9417249.png)

### 法二：windows特性

对于使用 `windows` 搭建的系统，可以通过 `windows` 流来绕过

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1644845087028-dd6efc77-a077-4429-8f02-72ea0857e683.png)

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1650726323618-c0e94302-e218-4d11-b66b-6d6398c847e8.png)

## 总结

本文只讲了两种特定情况下上传的方法，但是肯定还有其他的方式可以使用，本文仅做抛砖引玉。



`github` 链接：`https://github.com/d5shenwu/vulPOC`

