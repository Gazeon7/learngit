from multiprocessing import Process
import os
# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...'%(name, os.getppid()))  # 子进程调用getppid()方法获取父进程id

if __name__ == '__main__':
    print('Parent process %s'% os.getpid())
    p = Process(target= run_proc, args=('test',))
    print('child process will start')
    p.start()
    p1 = Process(target=run_proc, args=('test',))
    p1.start()




'''
如果要启动大量的子进程，可以用进程池的方式批量创建子进程
'''
from multiprocessing import Pool
import  os, time, random
def long_time_task(name):
    print(f'Run task {name}, {os.getpid()}')    # 子进程id
    start = time.time()
    time.sleep(random.random()*3)
    end = time.time()
    print(f'Task {name} runs %0.2f'%(end - start))
if __name__ == '__main__':
    print(f'Parent process {os.getpid()}')
    p = Pool(4)
    for i in range(5):
        p.apply_async(long_time_task, args = (i,))
    print('Waiting for all subprocesses done ....')
    p.close()
    p.join()
    print('All subprocess done')
    """
        对 Pool对象调用join()方法会等待所有子进程执行完毕，调用join()之前必须先调用close()，调用close()之后就不能继续添加
        新的Process了
        task0、1、2、3是立刻执行的，而task4 要等前面某个task完成后才执行，pool的默认大小是CPU的核数。
    """

'''
    子进程
    很多时候，子进程并不是自身，而是一个外部进程，我们创建了子进程后，还需要空值子进程的输入和输出。
    subprocess 模块可以让我们非常方便的启动一个子进程，然后控制其输入和输出。 
'''
# eg: 在python代码中运行命令nslookup www.python.org
import subprocess
print('$ nslookup www.python.org')
r = subprocess.call(['nslookup', 'www.baidu.com'])
print('Exit code:', r)

'''
如果子进程还需要输入，则可以通过communicate()方法输入：
'''
import subprocess
print('$nslookup')
p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
outoput, err = p.communicate(b'set q=mx\nbaidu.com\nexit\n')
print(outoput.decode('gbk'))
print('Exit code:', p.returncode)

'''
    进程之间通信、Process 之间肯定是需要通信的，操作系统提供了很多机制来实现进程间的通信。
    Python的multiprocessing模块包装了底层的机制，提供了Queue、Pipes等多种方式来交换数据。
    我们以Queue为例，在父进程中创建两个子进程，一个往Queue里写数据，一个从Queue里读数据：
'''
from multiprocessing import Process, Queue
import os, time, random
def write(q):
    print('Process to read:%s'%os.getpid())
    for value in ['A','B','C','D']:
        print(f'put {value} to queue...')
        q.put(value)
        time.sleep(random.random())
def read(q):
    print(f'Process to read{os.getpid()}')
    while True:
        value = q.get(True)
        print(f'Get{value} from queue')
if __name__ == '__main__':
    # 父进程创建queue，并传给各个子进程：
    q = Queue()
    pw = Process(target = write, args = (q,))
    pr = Process(target = read, args = (q,))
    # 启动子进程pw， 写入：
    pw.start()
    # 启动子进程pr， 读取：
    pr.start()
    # 等待pw结束
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止
    pr.terminate()