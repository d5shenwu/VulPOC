# Laravel三处全版本RCE链分析

## 0x00 漏洞环境

```
https://github.com/N0puple/php-unserialize-lib
```

进入对应的文件夹执行如下命令启动环境：

```
docker-compose up -d
```

访问 http://x.x.x.x/index.php/test ，看到 `hello world` 既搭建成功

测试代码

```php
<?php
namespace App\Http\Controllers;

class TestController extends Controller
{
	public function index()
	{
		if(isset($_GET['a']))
		{
			unserialize(base64_decode($_GET['a']));
		}
		else
		{
			echo "hello world";
		}
	}
}
```

## 0x02 漏洞分析

### 反序列化链1

使用 `laravel` 最常见的入口 `src/Illuminate/Broadcasting/PendingBroadcast.php::__destruct()` 

![](https://gitee.com/N0puple/picgo/raw/master/img/20220904144627.png)

`$this->events` 与 `$this->event` 可控，找某个类的 `dispatch` 方法，这里找到 `src/Illuminate/Bus/Dispatcher.php::dispatch($command)` 

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905205855.png)

`$this->queueResolver` 与 `$command` 可控，我们进入 `$this->commandShouldBeQueued($command)` ，查看代码

```php
protected function commandShouldBeQueued($command)
{
    return $command instanceof ShouldQueue;
}
```

因此需要传进来的 `$command` 是 `ShouldQueue` 的实例，而 `ShouldQueue` 是一个接口，因此只要是实现此接口的类的实例即可

 ![](https://gitee.com/N0puple/picgo/raw/master/img/20220905211326.png)

如上的都可以，此处选取 `BroadcastEvent`  类，然后进入 `$this->dispatchToQueue` 方法

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905224039.png)

`$connection` 为 `$command->connection` ，而 `$command` 是 `BroadcastEvent` 的实例，因此 `$connection` 可通过设置一个 `connection` 值来控制，而 `$this->queueResolver` 也是可控的，因此可以直接命令执行

### 反序列化链2

开局依旧是 `src/Illuminate/Broadcasting/PendingBroadcast.php::__destruct()` ，然后以 `__call` 入手，这里使用的是 `src/Illuminate/Validation/Validator.php::__call()` ，我们看到这里的代码

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905194557.png)

`$method` 是传进来的方法名，值为 `dispatch` ，`$parameters` 可控，`$method` 进入 `Str::snake` 进行一定的转换，然后返回，这里我们不用看代码，直接让 `dispatch` 进入得到返回值即可，不影响结果

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905195259.png)

可以看到，返回的 `$rule` 为空，接下来 `$this->extensions` 可控，我们进入 `$this->callExtension` 方法，第一个参数为空字符串，第二个参数可控

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905195450.png)

这里写的很明了，`$this->extensions` 可控，`$parameters` 也可控，直接可进入 `call_user_func_array($callback, $parameters);` ，并且可以命令执行

### 反序列化链3

同样的入口  `src/Illuminate/Broadcasting/PendingBroadcast.php::__destruct()`

```
public function __destruct()
{
    $this->events->dispatch($this->event);
}
```

找到 `src/Illuminate/Bus/Dispatcher.php::dispatch($command)` 

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905205855.png)

进入 `dispatchToQueue` 方法

![](https://gitee.com/N0puple/picgo/raw/master/img/20220905224039.png)

`$this->queueResolver` 可控，`$connection` 由 `$command` 得到，`$command` 也是可控的，因此都是可控的，因此可以执行任意类，我们找到如下位置

`Mockery\Loader\EvalLoader::load(MockDefinition $definition)` 

![](https://gitee.com/N0puple/picgo/raw/master/img/20220919143348.png)

在这里，很容易知道，我们要找到一个 `MockDefinition` 的实例化对象，接下来进入 `getClassName` 方法

```
public function getClassName()
{
    return $this->config->getName();
}
```

找到任意一个存在 `getName` 方法的类加进来就可以了

最后会使用到 `getCode()` 方法来获取值，然后 `eval` 执行，控制 `$this->code` 就可以执行任意代码。

```
public function getCode()
{
    return $this->code;
}
```

我在写链子的时候，`$command` 写的是另一个类，虽然某些版本可用，但是没法通杀，无奈最后用了 `phpggc` 中的 `RCE5` 中的，不得不说，该链子确实写的严谨，可以通杀所有版本。

## 0x03 漏洞复现

通过 `exp.php` 生成 `payload` ，然后直接打

![](https://gitee.com/N0puple/picgo/raw/master/img/20220904151025.png)



## 0x04 链接

目前在学代码审计，对此感兴趣的师傅可以加好友一起交流学习

环境与 `exp` 都可以在如下链接获取

### GitHub

https://github.com/N0puple/php-unserialize-lib

### GitBook:

https://n0puple.gitbook.io/php-unserialize-lib/

### 公众号

公众号搜索：安全漏洞复现

扫码持续关注：

![](https://gitee.com/N0puple/picgo/raw/master/img/qrcode_for_gh_a41358b842dd_430.jpg)

