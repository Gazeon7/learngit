def _odd_iter():
    """
    生成一个奇数序列
    :return:
    """
    n = 1
    while True:
        n = n + 2
        yield n
nums = _odd_iter()
def _not_divisible(n):
    """
    将n的倍数筛除
    :param n:
    :return:
    """
    return  lambda x: x % n !=0
def primes():
    """
    生成器：不断返回下一个素数
    :return:
    """
    yield 2
    it = _odd_iter()
    while True:
        n = next(it)
        yield n
        it = filter(_not_divisible(n), it)
for i in primes():
    if i < 1000:
        print(i)
    else:
        break

'''
回数是指从左向右读和从右向左读都是一样的数，例如12321，909。
请利用filter()筛选出回数：
'''

def is_palindrome(n):
    n = str(n)
    if n == n[::-1]:
        return n
output = filter(is_palindrome, range(1, 1000))
print('1~1000:', list(output))
if list(filter(is_palindrome, range(1, 200))) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, 44, 55, 66, 77, 88, 99, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191]:
    print('测试成功!')
else:
    print('测试失败!')
