# 创建class的方法就是用type()函数。type既可以返回一个对象的类型，又可以创建出新的类型，比如，我们可以通过type()函数创建hello类，而无需通过class Hello（object）的定义
def fn(self,name ='word'):
    print('hello,%s'%name)
Hello = type('Hello',(object,),dict(hello = fn))
h = Hello()
h.hello()
print(type(Hello))
print(type(h))
'''
type()依此传入3个参数：
1、class的名称
2、继承的父类集合，用元组格式保存
3、class的方法名称与函数绑定， dict(方法名 = 函数名)
'''


'''
元类  metaclass
定义了类后可以根据这个类创建出实例，所以：先定义类，然后创建实例
如果想创建出类，就必须根据metaclass创建出类，即先定义metaclass。然后定义class
类可以看作是元类的实例
'''
class ListMetaClass(type):
    """
    metaclass是类的模板，从type类型派生
    """
    def __new__(cls, name, bases, attrs):
        attrs['add'] = lambda self, value:self.append(value)
        return type.__new__(cls, name, bases, attrs)