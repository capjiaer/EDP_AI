# Python 装饰器（Decorator）详解教程

> 本文档详细解释 Python 装饰器的概念、原理和实际应用，特别是错误处理装饰器的使用。

---

## 📚 目录

1. [什么是装饰器？](#什么是装饰器)
2. [装饰器的基本概念](#装饰器的基本概念)
3. [装饰器的实现原理](#装饰器的实现原理)
4. [装饰器的常见用途](#装饰器的常见用途)
5. [错误处理装饰器详解](#错误处理装饰器详解)
6. [实际应用示例](#实际应用示例)
7. [总结](#总结)

---

## 什么是装饰器？

### 简单理解

**装饰器（Decorator）** 就像给函数"穿衣服"一样，在不修改函数本身代码的情况下，给函数添加额外的功能。

### 生活中的例子

想象一下：
- **原始函数** = 一个人
- **装饰器** = 给这个人穿上不同的衣服（功能）

比如：
- 穿上"安全帽"（错误处理装饰器）→ 这个人工作时如果出错，会自动处理
- 穿上"计时器"（性能监控装饰器）→ 这个人工作时会自动计时
- 穿上"日志记录器"（日志装饰器）→ 这个人工作时会自动记录日志

**关键点**：这个人（函数）本身没有变化，只是"穿上了衣服"（添加了功能）。

---

## 装饰器的基本概念

### 1. 函数是一等公民

在 Python 中，函数可以：
- 赋值给变量
- 作为参数传递
- 作为返回值返回
- 嵌套定义

```python
# 函数可以赋值给变量
def greet():
    return "Hello"

say_hello = greet  # 把函数赋值给变量
print(say_hello())  # 输出: Hello

# 函数可以作为参数传递
def call_function(func):
    return func()

print(call_function(greet))  # 输出: Hello

# 函数可以作为返回值返回
def get_greeter():
    return greet

greeter = get_greeter()
print(greeter())  # 输出: Hello
```

### 2. 装饰器的语法糖

装饰器有两种写法：

**写法 1：使用 `@` 符号（推荐）**
```python
@my_decorator
def my_function():
    pass
```

**写法 2：手动调用（等价）**
```python
def my_function():
    pass

my_function = my_decorator(my_function)
```

这两种写法**完全等价**！

---

## 装饰器的实现原理

### 最简单的装饰器

```python
def my_decorator(func):
    """最简单的装饰器"""
    def wrapper():
        print("函数执行前")
        result = func()  # 调用原始函数
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# 输出:
# 函数执行前
# Hello!
# 函数执行后
```

### 执行流程

```
1. Python 看到 @my_decorator
2. 调用 my_decorator(say_hello)
3. my_decorator 返回 wrapper 函数
4. say_hello 现在指向 wrapper 函数
5. 调用 say_hello() 时，实际执行的是 wrapper()
6. wrapper() 内部调用原始的 say_hello()
```

### 带参数的函数

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):  # 接收任意参数
        print("函数执行前")
        result = func(*args, **kwargs)  # 传递参数给原始函数
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

print(add(1, 2))
# 输出:
# 函数执行前
# 3
# 函数执行后
```

### 保留函数元信息

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 保留原始函数的元信息
    def wrapper(*args, **kwargs):
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

@my_decorator
def say_hello():
    """这是一个问候函数"""
    print("Hello!")

print(say_hello.__name__)  # 输出: say_hello（而不是 wrapper）
print(say_hello.__doc__)   # 输出: 这是一个问候函数
```

---

## 装饰器的常见用途

### 1. 计时装饰器

```python
import time
from functools import wraps

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.2f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"

slow_function()
# 输出: slow_function 执行时间: 1.00 秒
```

### 2. 日志装饰器

```python
from functools import wraps

def log(func):
    """日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用函数: {func.__name__}")
        print(f"[LOG] 参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] 返回值: {result}")
        return result
    return wrapper

@log
def add(a, b):
    return a + b

add(1, 2)
# 输出:
# [LOG] 调用函数: add
# [LOG] 参数: args=(1, 2), kwargs={}
# [LOG] 返回值: 3
```

### 3. 缓存装饰器

```python
from functools import wraps

def cache(func):
    """缓存装饰器"""
    cache_dict = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 用参数作为缓存键
        key = str(args) + str(kwargs)
        if key in cache_dict:
            print(f"[CACHE] 从缓存获取结果")
            return cache_dict[key]
        
        result = func(*args, **kwargs)
        cache_dict[key] = result
        print(f"[CACHE] 计算结果并缓存")
        return result
    return wrapper

@cache
def expensive_function(n):
    return n * n

print(expensive_function(5))  # 计算并缓存
print(expensive_function(5))  # 从缓存获取
```

---

## 错误处理装饰器详解

### 为什么需要错误处理装饰器？

**问题**：每个函数都要写重复的错误处理代码

```python
# 没有装饰器：每个函数都要写 try/except
def process_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"[ERROR] 文件未找到: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        return None

def process_data(data):
    try:
        return data.upper()
    except AttributeError as e:
        print(f"[ERROR] 属性错误: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        return None
```

**解决方案**：使用装饰器统一处理

```python
from functools import wraps

def handle_error(error_message="发生错误"):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[ERROR] {error_message}: {e}")
                return None
        return wrapper
    return decorator

@handle_error(error_message="处理文件失败")
def process_file(filename):
    with open(filename, 'r') as f:
        return f.read()

@handle_error(error_message="处理数据失败")
def process_data(data):
    return data.upper()
```

### EDP 框架中的错误处理装饰器

让我们看看 EDP 框架中的 `@handle_error` 装饰器：

```python
# edp_center/packages/edp_common/error_handler.py

def handle_error(
    error_message: Optional[str] = None,
    exit_code: int = 1,
    log_error: bool = True,
    reraise: bool = False,
    error_type: Optional[Type[Exception]] = None
):
    """
    错误处理装饰器
    
    统一处理函数中的异常，提供友好的错误输出和日志记录。
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except (error_type if error_type else Exception) as e:
                # 格式化错误消息
                if error_message:
                    msg = f"{error_message}: {e}"
                else:
                    msg = str(e)
                
                # 输出到 stderr
                print(f"[ERROR] {msg}", file=sys.stderr)
                
                # 如果是 EDPError，使用其格式化输出
                if isinstance(e, EDPError):
                    print(str(e), file=sys.stderr)
                else:
                    # 其他异常打印堆栈跟踪
                    traceback.print_exc()
                
                # 记录日志
                if log_error and logger:
                    if isinstance(e, EDPError) and log_exception:
                        log_exception(logger, e)
                    else:
                        logger.exception(msg)
                
                # 重新抛出或返回退出码
                if reraise:
                    raise
                
                # 返回退出码（CLI 命令通常返回退出码）
                return exit_code
        
        return wrapper
    return decorator
```

### 使用示例

**示例 1：抛出异常（reraise=True）**

```python
@handle_error(error_message="处理文件失败", reraise=True)
def process_tcl_file(config_file: Path, shared_interp: Tcl) -> Tcl:
    # 如果出错，装饰器会：
    # 1. 打印错误消息
    # 2. 记录日志
    # 3. 重新抛出异常（让调用者处理）
    shared_interp.eval(tcl_content)
    return temp_interp
```

**执行流程**：
```
1. 调用 process_tcl_file(...)
2. 装饰器 wrapper 执行
3. 如果出错：
   a. 打印 "[ERROR] 处理文件失败: ..."
   b. 记录日志
   c. 重新抛出异常（reraise=True）
4. 调用者可以捕获异常并处理
```

**示例 2：返回退出码（reraise=False）**

```python
@handle_error(error_message="执行命令失败", exit_code=1)
def my_command():
    # 如果出错，装饰器会：
    # 1. 打印错误消息
    # 2. 记录日志
    # 3. 返回退出码 1（不抛出异常）
    do_something()
    return 0
```

---

## 实际应用示例

### 统一前 vs 统一后

#### 统一前（每个函数都要写 try/except）

```python
def process_tcl_file(config_file: Path, shared_interp: Tcl) -> Tcl:
    abs_path = config_file.resolve()
    
    try:
        shared_interp.eval(tcl_content)
    except (RuntimeError, ValueError, SyntaxError) as e:
        print(f"[ERROR] Tcl 文件解析失败: {abs_path}", file=sys.stderr)
        print(f"[ERROR] 错误信息: {e}", file=sys.stderr)
        print(f"[ERROR] 请检查 Tcl 文件格式是否正确", file=sys.stderr)
        logger.error(f"Tcl 文件解析失败: {e}", exc_info=True)
        raise

def process_yaml_file(config_file: Path, shared_interp: Tcl) -> Optional[Tcl]:
    abs_path = config_file.resolve()
    
    try:
        config_dict = yaml.safe_load(yf) or {}
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML 文件解析失败: {abs_path}", file=sys.stderr)
        print(f"[ERROR] 错误信息: {e}", file=sys.stderr)
        print(f"[ERROR] 请检查 YAML 文件格式是否正确", file=sys.stderr)
        logger.error(f"YAML 文件解析失败: {e}", exc_info=True)
        raise
```

**问题**：
- ❌ 代码重复
- ❌ 错误处理逻辑不一致
- ❌ 难以维护

#### 统一后（使用装饰器）

```python
from edp_center.packages.edp_common.error_handler import handle_error
from edp_center.packages.edp_common.exceptions import ConfigError

@handle_error(error_message="Tcl 文件解析失败", reraise=True)
def process_tcl_file(config_file: Path, shared_interp: Tcl) -> Tcl:
    abs_path = config_file.resolve()
    try:
        shared_interp.eval(tcl_content)
    except (RuntimeError, ValueError, SyntaxError) as e:
        raise ConfigError(
            f"Tcl 文件解析失败: {e}",
            config_file=str(abs_path),
            suggestion="请检查 Tcl 文件格式是否正确"
        ) from e
    return temp_interp

@handle_error(error_message="YAML 文件解析失败", reraise=True)
def process_yaml_file(config_file: Path, shared_interp: Tcl) -> Optional[Tcl]:
    abs_path = config_file.resolve()
    try:
        config_dict = yaml.safe_load(yf) or {}
    except yaml.YAMLError as e:
        raise ConfigError(
            f"YAML 文件解析失败: {e}",
            config_file=str(abs_path),
            suggestion="请检查 YAML 文件格式是否正确"
        ) from e
    return temp_interp
```

**优势**：
- ✅ 代码简洁
- ✅ 统一的错误处理逻辑
- ✅ 易于维护

---

## 装饰器的执行顺序

### 多个装饰器

```python
@decorator1
@decorator2
@decorator3
def my_function():
    pass
```

**执行顺序**（从下往上）：
```
1. decorator3(my_function) → wrapper3
2. decorator2(wrapper3) → wrapper2
3. decorator1(wrapper2) → wrapper1
4. my_function 现在指向 wrapper1
```

**调用时**：
```
my_function() 
→ wrapper1() 
→ wrapper2() 
→ wrapper3() 
→ 原始 my_function()
```

### 实际例子

```python
@log
@timer
@handle_error
def my_function():
    return "Hello"

my_function()
# 执行顺序：
# 1. handle_error 的错误处理
# 2. timer 的计时
# 3. log 的日志记录
# 4. 执行原始函数
```

---

## 装饰器参数详解

### 1. 装饰器本身带参数

```python
def my_decorator(param1, param2):
    """装饰器本身带参数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"参数1: {param1}, 参数2: {param2}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@my_decorator("value1", "value2")
def my_function():
    pass
```

### 2. 装饰器不带参数

```python
def my_decorator(func):
    """装饰器不带参数"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def my_function():
    pass
```

### 3. 支持两种用法

```python
def my_decorator(func=None, *, param1=None, param2=None):
    """支持 @my_decorator 和 @my_decorator(...) 两种用法"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if param1:
                print(f"参数1: {param1}")
            return f(*args, **kwargs)
        return wrapper
    
    if func is None:
        # @my_decorator(param1="value")
        return decorator
    else:
        # @my_decorator
        return decorator(func)

# 用法1：不带参数
@my_decorator
def func1():
    pass

# 用法2：带参数
@my_decorator(param1="value")
def func2():
    pass
```

---

## 总结

### 装饰器的核心概念

1. **装饰器是函数**：接收函数作为参数，返回新函数
2. **不修改原函数**：原始函数代码不变，只是"包装"了一层
3. **语法糖**：`@decorator` 等价于 `func = decorator(func)`
4. **保留元信息**：使用 `@wraps` 保留原始函数的名称和文档

### 装饰器的优势

1. **代码复用**：相同的功能只需要写一次
2. **关注点分离**：业务逻辑和横切关注点（错误处理、日志等）分离
3. **易于维护**：修改装饰器就能影响所有使用它的函数
4. **代码简洁**：减少重复代码

### 错误处理装饰器的价值

1. **统一错误处理**：所有函数用相同的方式处理错误
2. **统一错误格式**：错误消息格式一致
3. **统一日志记录**：自动记录错误日志
4. **代码简洁**：不需要在每个函数中写 try/except

### 关键要点

- **装饰器是函数**：可以接收参数，可以嵌套
- **执行顺序**：多个装饰器从下往上执行
- **保留元信息**：使用 `@wraps` 保留原始函数信息
- **灵活使用**：根据需求选择合适的装饰器参数

---

## 进一步学习

- Python 官方文档：https://docs.python.org/3/glossary.html#term-decorator
- `functools.wraps`：https://docs.python.org/3/library/functools.html#functools.wraps
- 装饰器模式：设计模式中的装饰器模式

---

**希望这个教程帮助你理解 Python 装饰器！** 🎉

