
# 测试

## 测试

### 测试

#### 测试

##### 测试

###### 测试

Long long very long English? Long long very long English! Long long very long English. 

测试 latex 公式： $\frac 12$。

测试*强调*，**加重**。

测试超链接：[google](www.google.com)。

测试分界线:

-------------------------------

测试换行：   
测试行内代码 `test`。

测试图片：

![pic](img/Octocat.png)

测试外部图片：

![pic2](http://www.python.org/community/logos/python-logo.png)

测试代码块：

~~~~{.python}
def fib(n, memo={1: (0, 1, 1)}):
    if n in memo:
        return memo[n]
    a, b, c = fib(n/2)
    a, b, c = a*a+b*b, a*b+b*c, b*b+c*c
    if n & 1:
        a, b, c = b, c, b+c
    memo[n] = a, b, c
    return memo[n]
~~~~

测试表格：

left | right
-----|------
l1   | r1
l2   | r2
l3   | r3
