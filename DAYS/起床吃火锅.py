from types import MethodType


class student(object):
    __slots__ = ('name', 'sex', 'age')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.name}'


class gazeon(student):
    __slots__ = ('birth', 'addRice', 'bowls')

    def __init__(self, name):
        super().__init__(name=name)

    # def __getup__(self):
    #     print(f'{self.name} had get up!')
    def __getattr__(self, item):
        if item == 'getUp':
            print(f'{self.name} still sleeping, pls dont talk about that and be quiet')
        return g.hotPot('鸳鸯'), self.eating()

    @classmethod
    def hotPot(cls, kinds):
        print(f'gazeon is eating {kinds} hot pot!')

    @property
    def eat(self, bowls):
        self.bowls = bowls

    @eat.setter
    def eat(self):
        return self.bowls

    def eating(self):
        self.bowls = 0
        while self.bowls < 5:
            g.addRice()
            self.bowls += 1
            if self.bowls > 4:
                print(f'{self.name} cant eat more, {self.bowls} is enough')
                return


g = gazeon('gazeon')


def addRice(self):
    count = 1

    def adding(*args):
        nonlocal count
        print(f"{self.name}is adding rice, it's {count}th")
        count += 1
        return

    return adding


g.addRice = MethodType(addRice(self=g), g)
g.getUp
