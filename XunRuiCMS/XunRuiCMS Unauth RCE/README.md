## XunRui CMS Unauth RCE

### 漏洞简介

先后在两篇文章中看到了这个cms，利用方式感觉很有意思，遂跟着复现一波写下了这篇文章。

### 影响范围

影响在此修复之前的版本 https://gitee.com/dayrui/xunruicms/commit/80e2d8f3008384d926c64163b7334a260edc0a51

此处测试环境为修复的前一个版本，可 git 下载后执行命令

```php
git checkout fad7b01
```

### 漏洞利用

```
python3 xunrui_cms_unauth_RCE.py http://localhost calc.exe
```

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1644334744634-94e79d78-cf97-4ec2-a5a3-d576a8405421.png)

### 漏洞分析

https://www.cnsuc.net/thread-82.htm

