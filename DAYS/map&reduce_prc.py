'''
利用map()函数，把用户输入的不规范的英文名字，变为首字母大写，其他小写的规范名字。
输入：['adam', 'LISA', 'barT']，输出：['Adam', 'Lisa', 'Bart']：
'''
# L1 = ['adam', 'LISA', 'barT']
# def normalize(name: list) -> list:
#     for n in name:
#         return map(lambda name:name[0].upper()+name[1:].lower(),name)
# L = normalize(L1)
# for i in L:
#     print(i)
from functools import reduce


def normalize(name: str) -> str:
    return name[0].upper() + name[1:].lower()


L1 = ['adam', 'LISA', 'barT']
L2 = list(map(normalize, L1))
print(L2)

print('------------------------------------------')

"""
Python提供的sum()函数可以接受一个list并求和，
请编写一个prod()函数，可以接受一个list并利用reduce()求积：
"""


def prod(L: list) -> float:
    return reduce(lambda x, y: x * y, L)


print('3 * 5 * 7 * 9 =', prod([3, 5, 7, 9]))
if prod([3, 5, 7, 9]) == 945:
    print('测试成功!')
else:
    print('测试失败!')

print("-----------------------------------------")

"""
利用map和reduce编写一个str2float函数，
把字符串'123.456'转换成浮点数123.456：
"""


def str2float(num: str) -> float:
    if not isinstance(num, str):
        raise TypeError("there's a type error occurred, pls check your codes")
    num = list(num)
    idx = num.index('.')
    L1 = num[:idx]
    L2 = num[idx + 1:]
    f = reduce(lambda x, y: float(x) * 10 + float(y), L1)
    b = reduce(lambda x, y: float(x) / 10 + float(y), list(reversed(L2))) / 10
    return f + b


print('str2float(\'123.456\') =', str2float('123.456'))
if abs(str2float('123.456') - 123.456) < 0.00001:
    print('测试成功!')
else:
    print('测试失败!')
