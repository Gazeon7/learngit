import time
from datetime import datetime
import platform
from multiprocessing import cpu_count
from collections import namedtuple

import argparse
from pprint import pprint
from typing import Type

PROC_DISKSTATS = '/proc/diskstats'
PROC_STATS = '/proc/stat'
PROC_UPTIME = '/proc/uptime'
DATE = f"/{datetime.now().month}/{datetime.now().day}/{datetime.now().year}"
VERSION = '{} {} ({}) {:>19} _{}_         ({} CPU)'.format(platform.system(), platform.release(), platform.node(), DATE,
                                                           platform.machine(), cpu_count())
dev_status = namedtuple('dev_status', (
    'major_number', 'minor_number', 'device_name', 'rd_ios', 'rd_merges', 'rd_sectors', 'rd_ticks', 'wr_ios',
    'wr_merges', 'wr_sectors', 'wr_ticks', 'in_flight', 'io_ticks', 'time_in_queue'))
cpu_status = namedtuple('cpu_status',
                        ('user', 'nice', 'system', 'idle', 'io_wait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'))
dev_targets = namedtuple('dev_targets', ('Device', 'tps', 'r_s', 'w_s', 'rrqm_s', 'wrqm_s', 'rkB_s',
                                      'wkB_s', 'kB_read', 'kB_wrtn', 'avgrq_sz', 'avgqu_sz',
                                      'await_', 'r_await', 'w_await', 'svctm', 'util'))
cpu_targets = namedtuple('cpu_targets', ('user', 'nice', 'system', 'iowait', 'steal', 'idle'))


def handle_args():
    """
    解析参数
    :return:
    """
    parser = argparse.ArgumentParser(description='print status from CPU such as tps and so on.')
    parser.add_argument('-x', action='store_true', required=False, help='print status etailedly')
    parser.add_argument('-m', action='store_true', required=False, help='print status in MB')
    parser.add_argument('seconds', type=int, nargs='?', default=0, help='print status after seconds')
    parser.add_argument('device', type=str, nargs='?', default=None, help='print status which user ordered')
    _args = vars(parser.parse_args())
    return _args


def sys_time() -> float:
    """
    获取系统启动到现在的时间
    :return:
    """
    with open(PROC_UPTIME, 'r') as f:
        return float(f.read().strip('\n').split(' ')[0])


def proc_disk_tup(dev: str) -> (Type[namedtuple], datetime):
    """
    获取需要的磁盘信息
    :param dev: 磁盘名称
    :return:
    """
    res = []
    with open(PROC_DISKSTATS, 'r') as fd:
        while True:
            row = fd.readline().strip(' ').strip('\n').split(' ')  # 数据处理
            if dev in row:
                temp = [x for x in row if x != '']
                for val in temp:
                    try:
                        res.append(float(val.strip('\n')))
                    except ValueError:
                        res.append(val.strip('\n'))
                return dev_status._make(res), datetime.now()
            else:
                return None


def proc_stat_tup() -> Type[namedtuple]:
    """
    获取需要的CPU信息
    :return:
    """
    with open(PROC_STATS, 'r') as fd:
        fd.read(3)  # 读掉cpu序号
        cpu = fd.readline().strip(' ').strip('\n').split(' ')  # 数据处理
        return cpu_status._make([x for x in cpu if x != ''])  # 返回cpu命名元组


def dev_difference(old: dev_status, new: dev_status):
    """
    计算前后两次差值
    :param old: 第一次采样
    :param new: 第二次采样
    :return:
    """
    _old = dev_status._asdict(old)
    _new = dev_status._asdict(new)
    dif = []
    for o, n in zip(_old.values(), _new.values()):
        try:
            dif.append(round(float(n) - float(o), 2))
        except ValueError:
            dif.append(o)
    return dev_status._make(dif)


def cal_dev_targets(m: bool, interval: float, device: str, source_data, diff):
    """
    计算采样后各项指标
    :param interval: 采样周期
    :param source_data: 原数据
    :param diff: 采样
    :return:
    """
    divsor = 1024 if m else 1
    sys_t = sys_time()
    diff: dev_status
    source_data: dev_status
    res = dev_targets()
    dev_targets.Device = device
    dev_targets.tps = ((diff.rd_ios + diff.wr_ios) / sys_t / interval) if interval else (
                                                                                                    source_data.rd_ios + source_data.wr_ios) / sys_t
    dev_targets.r_s = (diff.rd_ios / sys_t / interval) if interval else (source_data.rd_ios / sys_t)
    dev_targets.w_s = (diff.wr_ios / sys_t / interval) if interval else (source_data.wr_ios / sys_t)
    dev_targets.rrqm_s = (diff.rd_merges / sys_t / interval) if interval else (source_data.rd_merges / sys_t)
    dev_targets.wrqm_s = (diff.wr_merges / sys_t / interval) if interval else (source_data.rd_merges / sys_t)
    dev_targets.rkB_s = (
                diff.rd_sectors / sys_t * (512 / 1024) / interval) if interval else source_data.rd_sectors / sys_t * (
                512 / 1024) / m
    dev_targets.wkB_s = (
                diff.wr_sectors / sys_t * (512 / 1024) / interval) if interval else source_data.rd_sectors / sys_t * (
                512 / 1024) / m
    dev_targets.kB_read = (diff.rd_sectors * (512 / 1024) / interval) if interval else source_data.rd_sectors * (
                512 / 1024) / m
    dev_targets.kB_wrtn = (diff.wr_sectors * (512 / 1024) / interval) if interval else source_data.wr_sectors * (
                512 / 1024) / m
    dev_targets.avgrq_sz = (diff.rd_sectors + diff.wr_sectors) / (diff.rd_ios + diff.wr_ios) if (
                diff.rd_ios + diff.wr_ios) else (source_data)
    dev_targets.avgqu_sz = (diff.time_in_queue / interval) if interval else source_data.time_in_queue
    dev_targets.await_ = ((diff.rd_ticks + diff.wr_ticks) / (diff.rd_ios + diff.wr_ios)) if (
                diff.rd_ios + diff.wr_ios) else (source_data.rd_ticks + source_data.wr_ticks) / (
                source_data.rd_ios + source_data.wr_ios)
    dev_targets.r_await = (diff.rd_ticks / diff.rd_ios) if diff.rd_ios else (source_data.rd_ticks / source_data.rd_ios)
    dev_targets.w_await = (diff.wr_ticks / diff.wr_ios) if diff.wr_ios else (source_data.wr_ticks / source_data.wr_ios)
    dev_targets.util = (diff.io_ticks / sys_t / interval) if interval else (source_data.io_ticks / sys_t)
    dev_targets.svctm = (dev_targets.util / dev_targets.tps) if dev_targets.tps else dev_targets.util



def cpu_info(old_cpu_data, new_cpu_data):
    """
    计算cpu各参数采样差值
    :return:
    """

    old_cpu: cpu_status = old_cpu_data
    new_cpu: cpu_status = new_cpu_data
    total = cpu_status.user + cpu_status.nice + cpu_status.system + cpu_status.io_wait + cpu_status.idle
    cpu_targets.user = (new_cpu.user - old_cpu.user) / total * 100
    cpu_targets.nice = (new_cpu.nice - old_cpu.nice) / total * 100
    cpu_targets.system = (new_cpu.system - old_cpu.system) / total * 100
    cpu_targets.iowait = (new_cpu.io_wait - old_cpu.io_wait) / total * 100
    cpu_targets.idle = (new_cpu.idle - old_cpu.idle) / total * 100


def format_out_put(x: bool, m: bool, cpu_info: cpu_targets, dev_info: dev_targets):
    print(VERSION)
    print('avg-cpu:  %user   %nice %system %iowait  %steal   %idle')
    print('{:>15} {:>7} {:>7} {:>7} {:>7} {:>7}'.format(cpu_info.user, cpu_info.nice, cpu_info.system, cpu_info.iowait,
                                                        cpu_info.steal, cpu_info.idle))
    if x and m:
        print(
            'Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util')
        print('{:<18} {:<7} {:<7} {:<7} {:<9} {:<8} {:<10} {:<5} {:<10} {:<7} {:<7} {:<4} {:<6} {}'.format(dev_info.Device,
            dev_info.rrqm_s, dev_info.wrqm_s, dev_info.r_s, dev_info.w_s, dev_info.rkB_s, dev_info.wkB_s,
            dev_info.avgrq_sz, dev_info.avgqu_sz, dev_info.await_, dev_info.r_await, dev_info.w_await, dev_info.svctm,
            dev_info.util))
    elif x and not m:
        pass
    elif not x and m:
        pass
    else:
        pass
def main():
    args = handle_args()
    source_data, _ = proc_disk_tup(args['device'])
    # old_cpu = proc_stat_tup()
    # old, old_time = proc_disk_tup(args['device'])
    # time.sleep(args['seconds'])
    # new, new_time = proc_disk_tup(args['device'])
    # new_cpu = proc_stat_tup()
    # dif = dev_difference(old, new)
    # interval = float(datetime.timestamp(new_time) - datetime.timestamp(old_time))
    # cal_dev_targets(args['m'], interval, args['device'], source_data, dif)
    # cpu_info(old_cpu, new_cpu)
    # c = cpu_targets
    # format_out_put(args['x'], args['m'], cpu_targets, dev_targets)
    print(source_data)
# _dev_targets = dev_targets()

if __name__ == '__main__':
    main()