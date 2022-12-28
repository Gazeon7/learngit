'''
线程是操作系统直接支持的执行单元。
Python的标准库提供了两个模块：_thread和threading， _thread 是低级模块， threading是高级模块，对_thread进行了封装。
绝大多数情况下，我们只需要使用threading这个高级模块
启动一个线程就是把一个函数传入并创建Thread实例，然后调用start()开始执行：
'''
import time, threading
def loop():
    print(f'threa{threading.currentThread().name}') # current_thread()函数，永远返回当前线程的实例。
    n = 0
    while n < 5:
        n += 1
        print(f'thread {threading.currentThread().name} >>>{n}')
        time.sleep(1)
    print(f'thread{threading.currentThread().name}')
print(f'threading{threading.currentThread().name}')
t = threading.Thread(target=loop, name = 'LoopThread')
t.start()
t.join()
print(f'thread{threading.currentThread().name} enden.')

# Lock
'''
多线程和多进程最大的不同：多进程中，同一个变量，各自有一份拷贝存在于每个进程中，互不影响，而多线程中，所有变量都由线程
共享。所以任何一个变量都可以被任何一个线程修改，因此，线程之间共享数据最大的危险载语多个线程同时修改一个变量，把内容改乱了
'''
# multithread
# 假定这是你的银行存款：
balance = 0
def change_it(n):
    # 先存后驱，结果应该为0：
    global balance
    balance = balance + n
    balance = balance - n

#
lock = threading.Lock()

def run_thread(n):
    for i in range(100000):
        # 先要获取锁
        lock.acquire()
        try:
            #放心的改吧
            change_it(n)
        finally:
            #改完了一定要释放锁
            lock.release()
t1 = threading.Thread(target=run_thread, args=(5,))
t2 = threading.Thread(target=run_thread, args=(8,))
t1.start()
t2.start()
t1.join()
t2.join()
print(balance)
'''
如果我们要确保balance计算正确，就要给change_it()上一把锁，当某个线程开始执行change_it()的时，我们说，因为该线程获得
了锁，因此其他线程不能同时执行change_it()，只能等待，直到锁被释放以后，获得该锁以后才能更改。由于锁只有一个，无论多少线程，
同一时刻最多只有一个线程持有该锁，所以，不会造成修改的冲突。创建一个锁通过threading().lock()来实现:
'''
'''
当多个线程同时执行lock.acquire()时，只有一个线程成功的获取锁，然后继续执行代码，其他线程就继续等待直到获得锁为止。
获得锁的线程用完后一定要释放锁，否则那些苦苦等待锁的线程将永远等下去，成为死线程，所以我们用try...finally来确保锁一定会被
释放。
锁的好处就是确保了某段关键代码只能由一个线程从头到尾完整地执行，坏处当然也很多，首先是阻止了多线程并发执行，包含锁的某段代码
实际上只能以单线程模式执行，效率就大大地下降了。其次，由于可以存在多个锁，不同地线程持有不同地锁，并试图获取对方持有地锁时，
可能会造成死锁。导致多个线程全部挂起，既不能执行，也无法结束，只能靠操作系统强行终止。
'''