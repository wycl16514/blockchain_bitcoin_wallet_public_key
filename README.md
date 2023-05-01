
前两节我们探讨了抽象代数的重要概念：有限域，然后研究了基于椭圆曲线上点的怪异”+“操作，两者表面看起来牛马不相及，实际上两者在逻辑上有着紧密的联系，简单来说如果我们在椭圆曲线上取一点G,然后让它跟自己做”+“操作，那么所得结果形成的集合就会构成有限域。

首先我们先给定一个有限域F(103)={0, 1, .... 102}, 同时回忆一下我们前面讲过作用在有限域上的"+"和"*"两种操作其实对应在求余基础上普通的加法和乘法，由此我们判断有限域中某个点是否在给定椭圆曲线y ^ 2 = x ^ 3 + 7：上时，首先把该点的x,y坐标代入椭圆曲线方程，同时在求余的基础上判断左右两边是否相等，例如判断点(17, 64)(这里x,y坐标的值都从有限域F(103)中获取)是否在曲线上，我们做如下计算：
 y ^ 2 = (64 ^ 2) % 103 = 79,  x ^ 3 + 7 = (17 ^ 3 + 7 ) % 103 = 79
 由于左右两边计算后取值相同，因此点(17, 64)在曲线上。

我们把有限域的"+"和" \* " 两种运算跟上一节我们提到的椭圆曲线上点的"+"操作结合起来就能起到加密效果，这里要注意我们不要把两种操作混淆，因为他们对应的符号看起来一样，但实际对应的运算不一样。

首先我们把上面提到的有限域点在椭圆曲线上的判断逻辑用代码实现一下看看：
```python
"""
将有限域的点输入到椭圆曲线，需要注意的是在椭圆曲线里执行+和*两种运算时，它会自动转换为
有限域定义的__add__ 和 __mul__运算，注意到即使运算操作的逻辑变了，但是判断点是否在椭圆曲线上
依然是判断椭圆曲线对应公式的两边是否相等
"""

a = LimitFieldElement(0, 223)
b = LimitFieldElement(7, 223)
x = LimitFieldElement(192, 223)
y = LimitFieldElement(105, 223)
p1 = EllipticPoint(x, y, a, b)
print(f"Elliptc Point over F_223 is {p1}")
```
上面代码运行后所得结果为：
Elliptc Point over F_223 is EllipticPoint(x:LimitFieldElement_223(192),y:LimitFieldElement_223(105),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))

这里需要注意，在执行EllipticPoint(x, y, a, b)这条语句时，它对应的__init__函数会被执行，里面会对输入参数执行如下运算：
```python
if y ** 2 != x ** 3 + a * x + b:
```
这里相应操作例如 "**", "*", "+" , "!="对应到有限域对象中的\___pow\___,  \___mul\___ , \___add\___, \___ne\___，这几个重载函数。

现在来点烧脑的，上一节我们推导了椭圆曲线上给定两点，如何得出他们执行"+"运算后所得的第3点，在算法中执行了一系列普通加减乘除运算，现在我们把这些运算全部转换为有限域上对应的运算，所得结果依然成立，例如给定两点P1(x1,y1), P2(x2, y2),要获得P3 = P1 + P2,我们在上一节执行了如下运算：
```python
s = (y2 - y1)/(x2 - x1)
x3 = s ^ 2 - x1 - x3
y3 = s * (x1 - x3) - y1
```
上面的减法要对应到LimitFiniteField类的__sub__ ，”\____truediv\____“等逻辑实现。这里可以体会到，我们把普通的加减乘法运算换成带求余操作的运算后，原有结论依然成立，这就是抽象代数的强大作用。前面章节中我忘了实现LimitFinitField类中的__ sub __ , __ rmul __ 两个方法， 他们的实现如下：
```python
 def __sub__(self, other):
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域的元素执行减法操作")
        num = (self.num - other.num) % self.order
        return __class__(num, self.order)
   
def __rmul__(self, scalar):
        #实现与常量相乘
        num = (self.num * scalar) % self.order
        return __class__(num, self.order)
```

有了上面基础后，我们测试一下在有限域基础上椭圆曲线上点的”+“操作，代码如下：
```python
```a = LimitFieldElement(0, 223)
b = LimitFieldElement(7, 223)
x = LimitFieldElement(192, 223)
y = LimitFieldElement(105, 223)
p1 = EllipticPoint(x, y, a, b)
#print(f"Elliptc Point over F_223 is {p1}")

#基于有限域上椭圆曲线点对应的"+"操作
x2 = LimitFieldElement(17, 223)
y2 = LimitFieldElement(56, 223)
p2 = EllipticPoint(x2, y2, a, b)

print(f"Elliptic point P1 + P2 is {p1 + p2}")
```
上面代码运行后所得结果如下：
```python 
Elliptic point P1 + P2 is EllipticPoint(x:LimitFieldElement_223(170),y:LimitFieldElement_223(142),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))

```

下面我们要实现椭圆曲线点与常量的乘法，这个操作将对椭圆曲线加密产生重要作用，后面我们会选取椭圆曲线上一点G, 然后选取一个常量k, 计算 k*G，其中k对应的就是私钥，而k*G对应的就是公钥。这里基于一个原理是，即使让你知道点G, 同时给你k*G的结果，在数学上也没有办法能够逆向计算出k来，于是这点就成为了椭圆曲线加密的原理。

下面我们用代码实现一下椭圆曲线上给定一点G，然后计算k*G，, k = 1, 2, ....所得结果，注意到常量乘法本质上是把G跟自己相加给定次数：
```python
#计算点G(47, 71)的常量乘法
x = LimitFieldElement(47, 223)
y = LimitFieldElement(71, 223)
G = EllipticPoint(x, y, a, b)
result = G
for k in range(1, 22):
    if k != 1:
        result = result + G
    print(f"{k} * (47, 71) is {result}")
```
上面代码运行后所得结果如下：
```python
1 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(47),y:LimitFieldElement_223(71),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
2 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(36),y:LimitFieldElement_223(111),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
3 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(15),y:LimitFieldElement_223(137),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
4 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(194),y:LimitFieldElement_223(51),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
5 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(126),y:LimitFieldElement_223(96),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
6 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(139),y:LimitFieldElement_223(137),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
7 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(92),y:LimitFieldElement_223(47),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
8 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(116),y:LimitFieldElement_223(55),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
9 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(69),y:LimitFieldElement_223(86),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
10 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(154),y:LimitFieldElement_223(150),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
11 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(154),y:LimitFieldElement_223(73),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
12 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(69),y:LimitFieldElement_223(137),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
13 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(116),y:LimitFieldElement_223(168),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
14 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(92),y:LimitFieldElement_223(176),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
15 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(139),y:LimitFieldElement_223(86),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
16 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(126),y:LimitFieldElement_223(127),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
17 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(194),y:LimitFieldElement_223(172),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
18 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(15),y:LimitFieldElement_223(86),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
19 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(36),y:LimitFieldElement_223(112),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
20 * (47, 71) is EllipticPoint(x:LimitFieldElement_223(47),y:LimitFieldElement_223(152),a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
21 * (47, 71) is EllipticPoint(x:None,y:None,a:LimitFieldElement_223(0), b:LimitFieldElement_223(7))
```
上面的运行结果有一个特点，那就是当k增加到21时，k\*G 所得结果是椭圆曲线的0点，椭圆曲线上任取一点执行如上操作都会得到这样的结果，当k=1开始，一直到k=n使得k \* G 为零点时，那么集合{0，G, 2*G, .... ,(n-1)*G}所形成的集合在数学上称为”群“。

相比于前面我们提到的有限域，群中的元素只对应一种操作"+"(有限域有两种)，下面我们看看群的一些性质：
1，单位0，也就是群中必然包含一个特殊元素"0"，任何元素跟他执行”+“操作，其结果都是该元素自己，也就是如果A是群中任何一个元素，那么A "+" 0 = A, 
2，闭合性，如果A, B是群中两个元素，那么A "+" B 所得结果还是群中的元素。
3，可逆性，如果A是群中的一个元素，那么群中比如存在另一个元素B, 使得A "+" B = 0
4，交换性，如果A, B是群中两个元素，那么有 A "+" B = B "+" A
5，关联性，(A "+" B) "+" C = A "+" (B "+" C)

"群“是抽象代数中一个至关重要的概念，它也是密码学的支柱性概念。前面我们实现k \* G时，代码是把G点执行k次"+"操作，现在我们给椭圆曲线的点添加常量乘法，在EllipitcPoint中增加代码实现如下：
```python
 def __rmul__(self, scalar):
        #如果常量是0，那么就返回椭圆曲线"0"点
        result = self.__class__(None, None, self.a, self.b)
        #自加给定次数
        for _ in range(scalar):
            result += self

        return result
```
我们用如下代码测试一下上面的实现，可以发现输出结果跟原来一样，由此能确认实现的正确性：
```python
#测试常量乘法：
for k in range(1, 22):
    print(f"{k} * (47, 71) is {k * G}")
```
接下来我们看比特币对应椭圆曲线的实现，对于比特币而言，它对应的椭圆曲线就是设置a = 0, b = 7, 因此它对应的曲线公式就是 y ^ 2 = x ^ 3 + 7，对比特币而言，它定义的有限域中元素个数为p = 2256 – 232 – 977, 同时G点的x分量为 G(x) = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
G(y) = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
当k =  0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141时，k \* G = 0。

对于比特币使用的椭圆曲线，它有几个特点，首先是参数a, b非常简单，其次它对应有限域中元素个数及其多，接近2 ^ 256，所以椭圆曲线G点两个分量大小都接近256bit，也就是32字节，这个数值几乎接近了全宇宙的原子总数。

下面我们用代码看看G点是否在比特币曲线上：
```python
#测试G点是否在曲线上
gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
p = 2 ** 256 - 2 ** 32 - 977
print(gy ** 2 % p == (gx ** 3 + 7) % p) #True
```
上面代码运行后返回True。下面我们尝试把G点的两个分量转换为有限域上的点，同时测试一下k \* G 的结果是否为椭圆曲线上的0点，相应代码如下：
```python
k = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
x = LimitFieldElement(gx, p)
y = LimitFieldElement(gy, p)
a = LimitFieldElement(0, p)
b = LimitFieldElement(7, p)
G = EllipticPoint(x, y, a, b)
print(f'result of n * G is {n * G}')
```
如果直接执行上面代码你会发现程序会卡死，原因在于k的值实在太大，我们在实现EllipticPoint类的常量乘法时(__ rmul __)，使用的是循环k次加法，但由于k的值实在太大，因此循环无法在短时间内完成。

一种解决办法是使用二进制扩展来优化，我们看个具体例子，假设常量值k的值为36，它转换为二进制就是100100，于是k * G = (2 ^5 +  2 ^ 2) * G = 2 ^ 5 * G + 2 ^ 2 * G，这里可以看到我们把原来36次加法转换成2次乘法和1次加法，所需计算量不超过lg(k)，注意到在计算(0b100100) * G时，我们从最右边的比特位开始遍历，如果比特位是0，那么我们只需要计算2 ^ k （k表示当前遍历的比特位在二进制中的位置)，如果遍历到的比特位是1，那么就执行一次加法，于是我们把常量乘法进行如下优化：
```python
    def __rmul__(self, scalar):
        #二进制扩展
        coef = scalar
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1: #如果当前比特位是1，那么执行加法
                result += current
            current += current  #如果上次比特位的位置在k，那么下次比特位的位置变成k+1，2^(k+1)*G 等价于2^k*G + 2^k * G
            coef >>= 1

        return result
```
经过如上优化后再执行前面的代码，所得结果如下：
```python
result of k * G is EllipticPoint(x:None,y:None,a:LimitFieldElement_115792089237316195423570985008687907853269984665640564039457584007908834671663(0), b:LimitFieldElement_115792089237316195423570985008687907853269984665640564039457584007908834671663(7))

```
可以看到 k \* G的结果确实是椭圆曲线上的零点。由于比特币对应的椭圆曲线叫secp256k1,其中曲线的a,b参数等已经确定，同时有限域元素个数也确定，因此我们在LimitFinitField和EllipticPoint的基础上做对应子类，把相应参数给写死，代码如下：
```python

P = 2**256 - 2**32 - 977


class S256Field(LimitFieldElement):
    def __init__(self, num, order=None):
        # 参数写死即可
        super().__init__(num, P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)


N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


class S256Point(EllipticPoint):
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(0), S256Field(7)
        if type(x) == int:
            super().__init__(S256Field(x), S256Field(y), a, b)
        else:
            # 如果x,y 是None，那么直接初始化椭圆曲线的0点
            super().__init__(x, y, a, b)

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'

        return f'S256Point({self.x}, {self.y})'

    def __rmul__(self, k):
        k = k % N
        return super().__rmul__(k)


G = S256Point(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
              0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)


print(N * G)
```
上面代码运行后输出结果为：
```python
S256Point(infinity)
```

有了以上基础后，我们就可以通过椭圆曲线生成公钥和私钥，私钥很简单，我们只要在[1, N]这个范围内取一个值e即可，然后公钥就是P = e * G，有了公钥，我们就可以构建比特币钱包的地址。

更多内容请在B站搜索coding迪斯尼。本节代码下载地址为：

链接: https://pan.baidu.com/s/1SIVPmmVXYnA0pfKh4cfuEQ 提取码: b1fe
