from enum import Enum, unique

Month = Enum('Month',('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'))
print(Month.Jan.value)
@unique
class WeekDay(Enum):
    Sun = '礼拜天'
    Mon = '礼拜一'
    Tue = '礼拜二'
    Wed = '礼拜三'
    Thu = '礼拜四'
    Fri = '礼拜五'
    Sat = '礼拜六'
print(WeekDay.Sun.value)
print(WeekDay['Mon'])
print(WeekDay('礼拜二'))



"""
把studen的genbder属性改为枚举类型，可以避免使用字符串：
"""


class Gender(Enum):
    MALE = 0
    FAMLE = 1

class Student(object):
    def __init__(self, name, gender):
        self.name =name
        self.gender = Gender.MALE

bart = Student('Bart',Gender.MALE)
if bart.gender == Gender.MALE:
    print('sada ')