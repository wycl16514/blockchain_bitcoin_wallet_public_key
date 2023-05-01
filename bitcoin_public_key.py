class LimitFieldElement:  # 实现有限域的元素
    def __init__(self, num, order):
        """
        order 表示集合元素的个数，它必须是一个素数，不然有限域的性质不能满足
        num 对应元素的数值
        """

        if order <= num < 0:
            err = f"元素 {num} 数值必须在0到 {order - 1} 之间"
            raise ValueError(err)
        self.order = order
        self.num = num

    def __repr__(self):
        return f"LimitFieldElement_{self.order}({self.num})"

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.order == other.order

    def __ne__(self, other):
        if other is None:
            return True

        return self.num != other.num or self.order != other.order

    def __add__(self, other):
        """
        有限域元素的"+"操作，它是在普通加法操作的基础上，将结果对集合中元素个数求余
        """
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行+操作")
        # 先做普通加法，然后在结果基础上相对于集合元素的个数做求余运算
        num = (self.num + other.num) % self.order
        """
        这里使用__class__而不是LimitFieldElemet是为了后面实现类的继承考虑，
        后面我们实现的对象需要继承与这个类
        """
        return self.__class__(num, self.order)

    def __sub__(self, other):
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域的元素执行减法操作")
        num = (self.num - other.num) % self.order
        return __class__(num, self.order)

    def __mul__(self, other):
        """
        有限域元素进行"*"操作时，先执行普通的乘法操作，然后将结果针对集合元素的个数进行求余
        """
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行*操作")

        num = (self.num * other.num) % self.order
        return self.__class__(num, self.order)

    def __pow__(self, power, modulo=None):
        """
        指数操作是先执行普通四则运算下的指数操作，再将所得结果针对集合元素个数求余
        """
        while power < 0:
            power += self.order
        num = pow(self.num, power, self.order)
        return self.__class__(num, self.order)

    def __truediv__(self, other):
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行*操作")
        # 通过费马小定理找到除数的对应元素
        #negative = (other.num ** (self.order - 2)) % self.order
        #这里必须使用系统提供的pow函数，因为它经过了算法优化，我们上面直接算，当数值很大时效率很低，代码会卡住
        negative = pow(other.num, self.order - 2, self.order)
        num = (self.num * negative) % self.order
        return self.__class__(num, self.order)

    def __rmul__(self, scalar):
        #实现与常量相乘
        num = (self.num * scalar) % self.order
        return __class__(num, self.order)


class EllipticPoint:
    def __init__(self, x, y, a, b):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        """
        x == None, y == None对应点"0"
        """
        if x is None or y is None:
            return

        """
        a, b为椭圆曲线方程 y^2 = x ^ 3 + ax + b
        对于区块链的椭圆曲线a取值为0，b取值为7,其专有名称为secp256k1
        由此在初始化椭圆曲线点时，必须确保(x,y)位于给定曲线上
        """
        t = y ** 2
        t = x ** 3
        t = a * x
        if y ** 2 != x ** 3 + a * x + b:
            raise ValueError(f'({x}, {y}) is not on the curve')

    def __eq__(self, other):
        """
        两个点要相等，我们不能只判断x,y是否一样，必须判断他们是否位于同一条椭圆曲线
        """
        return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.a != other.a or self.b != other.b

    def __add__(self, other):
        if self == other and self.y == 0 * self.x:
            #对应椭圆曲线顶部点的切线
            return self.__class__(None, None, self.a, self.b)

        """
        实现"+"操作，首先确保两个点位于同一条曲线，也就是他们对应的a,b要相同
        """
        if self.a != other.a or self.b != other.b:
            raise TypeError(f"points {self}, {other} not on the same curve")

        # 如果其中有一个是"0"那么"+"的结果就等于另一个点
        if self.x is None:
            return other
        if other.x is None:
            return self

        """
        两点在同一直线上，也就是x相同，y不同
        """
        if self.x == other.x and self.y != other.y:
            return __class__(None, None, self.a, self.b)

        """
        计算两点连线后跟曲线相交的第3点，使用韦达定理
        """
        x1 = self.x
        y1 = self.y
        x2 = other.x
        y2 = other.y
        if self == other:
            # 如果两点相同，根据微分来获得切线的斜率
            t1 = 3 * self.x ** 2 + self.a
            t2 = 2 * self.y
            t3 = t1 / t2
            k = (3 * self.x ** 2 + self.a) / (2 * self.y)
        else:
            k = (y2 - y1) / (x2 - x1)

        x3 = k ** 2 - x1 - x2
        y3 = k * (x1 - x3) - y1

        return __class__(x3, y3, self.a, self.b)

    def __repr__(self):
        return f"EllipticPoint(x:{self.x},y:{self.y},a:{self.a}, b:{self.b})"

    # def __rmul__(self, scalar):
    #     #如果常量是0，那么就返回椭圆曲线"0"点
    #     result = self.__class__(None, None, self.a, self.b)
    #     #自加给定次数
    #     for _ in range(scalar):
    #         result += self
    #
    #     return result

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





