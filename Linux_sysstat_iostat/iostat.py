import platform
import time
from datetime import datetime
import argparse

proc_disk_stats = '/proc/diskstats'
proc_stat = '/proc/stat'
proc_uptime = '/proc/uptime'
date = str(datetime.now().year) + '年' + str(datetime.now().month) + '月' + str(datetime.now().day) + '日'


def handle_args():
    parser = argparse.ArgumentParser(description='print status from CPU such as tps and so on.')
    parser.add_argument('-x', action='store_true', help='print status etailedly')
    parser.add_argument('-m', action='store_true', help='print status in MB')
    parser.add_argument('device', type=str, nargs='?', default=None, help='print status which user ordered')
    parser.add_argument('seconds', type=int, nargs='?', default=0, help='print status after seconds')
    _args = vars(parser.parse_args())
    return _args


def sys_time() -> list:
    """
    获取系统启动到现在的时间和系统空闲时间
    :return:
    """
    with open(proc_uptime, 'r') as f:
        return f.read().strip('\n').split(' ')


def title():
    """
    输出令第一行系统信息
    :return:
    """
    return f'{platform.system()} {platform.release()} ({platform.node()})         {date}  _{platform.machine()}_    '


def get_proc_diskstats():
    with open(proc_disk_stats, 'r') as fd:
        disk_stats = fd.readlines()
        res = []
        row = []
        for vals in disk_stats:
            # print(vals)
            temp = (vals.split(' '))
            # print(temp)
            for ele in temp:
                if ele != '':
                    row.append(ele)
                    # print(row)
            res.append(row)
            # print(row)
            row = []  # 重置为空存放下一行
            # print(temp)
        # print(res)
        return res


def get_proc_stat():
    res = []
    with open(proc_stat, 'r') as f:
        while True:
            if 'cpu' in f.read(5):
                # f.seek(5, SEEK_SET)
                res.append(f.readline().strip().strip('\n').split(' '))
            else:
                break
    return res


def diskstats_targets() -> dict:
    data = get_proc_diskstats()
    res_dict = {
        'major_number': [],  # 主设备号
        'minor_number': [],  # 次设备号
        'device_name': [],  # 设备名称
        'rd_ios': [],  # read_completed_successfully   3读操作的次数
        'rd_merges': [],  # 合并读操作的次数
        'rd_sectors': [],  # 读取的扇区数量
        'rd_ticks': [],  # 读操作消耗的时间  以毫秒为单位
        'wr_ios': [],  # 写操作的次数
        'wr_merges': [],  # 合并写操作的次数
        'wr_sectors': [],  # 写入的扇区数量
        'wr_ticks': [],  # 写操作消耗的时间  以毫秒为单位
        'in_fligth': [],  # 当前未完成的I/O数量
        'io_ticks': [],  # 该设备用于处理I/O的自然时间(wall-clock time)
        'time_in_queue': []  # 对字段#13(io_ticks)的加权值
    }

    for ind, val in enumerate(data):
        # print(val)
        res_dict['major_number'].append(float(val[0]))
        res_dict['minor_number'].append(float(val[1]))
        res_dict['device_name'].append(val[2])
        res_dict['rd_ios'].append(float(val[3]))
        res_dict['rd_merges'].append(float(val[4]))
        res_dict['rd_sectors'].append(float(val[5]))
        res_dict['rd_ticks'].append(float(val[6]))
        res_dict['wr_ios'].append(float(val[7]))
        res_dict['wr_merges'].append(float(val[8]))
        res_dict['wr_sectors'].append(float(val[9]))
        res_dict['wr_ticks'].append(float(val[10]))
        res_dict['in_fligth'].append(float(val[11]))
        res_dict['io_ticks'].append(float(val[12]))
        res_dict['time_in_queue'].append(float(val[13].strip('\n')))
    return res_dict


def stat_targets() -> dict:
    data = get_proc_stat()
    res_dict = {
        'user': [],  # 从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。
        'nice': [],  # 从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间
        'system': [],  # 从系统启动开始累计到当前时刻，处于核心态的运行时间
        'idle': [],  # 从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间
        'iowait': [],  # 从系统启动开始累计到当前时刻，IO等待时间
        'irq': [],  # 从系统启动开始累计到当前时刻，硬中断时间
        'softirq': [],  # 从系统启动开始累计到当前时刻，软中断时间
        'steal': [],  # 在虚拟环境中运行时，在其他操作系统上花费的时间是多少
        'guest': [],  # 在Linux内核的控制下为客户操作系统运行虚拟CPU的时间
        'guest_nice': []  # 修改优先级进程的运行时间
    }
    for ind, val in enumerate(data):
        res_dict['user'].append(val[0]),
        res_dict['nice'].append(val[1]),
        res_dict['system'].append(val[2]),
        res_dict['idle'].append(val[3]),
        res_dict['iowait'].append(val[4]),
        res_dict['irq'].append(val[5]),
        res_dict['softirq'].append(val[6]),
        res_dict['steal'].append(val[7]),
        res_dict['guest'].append(val[8]),
        res_dict['guest_nice'].append(val[9])
    return res_dict


def device_data(_interval) -> dict:
    """
    输出device所需的值到字典
    :param _interval: 时间间隔
    :return:
    """
    old_disk_stats_data = diskstats_targets()
    new_disk_stats_data = diskstats_targets()
    sys_start_time, sys_idle_time = float(sys_time()[0]), float(sys_time()[1])  # 系统启动到现在的时间和系统空闲时间
    device_targets = ('Device', 'tps', 'r/s', 'w/s', 'rrqm/s', 'wrqm/s', ('kB_read/s', 'MB_read/s', 'rkB/s'),
                      ('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s'),
                      ('kB_read', 'MB_read'), ('kB_wrtn', 'MB_wrtn'), 'avgrq-sz', 'avgqu-sz',
                      'await', 'r_await', 'w_await', 'svctm', '%util')
    device_dic = {}
    for key in device_targets:
        device_dic[key] = []
    device_dic['Device'] = new_disk_stats_data['device_name']
    for ind, val in enumerate(device_dic['Device']):
        device_dic['tps'].append(
            round((((new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind]) + (
                    new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind])) / sys_start_time / _interval)
                  if _interval else (old_disk_stats_data['rd_ios'][ind] +old_disk_stats_data['wr_ios'][ind]) / sys_start_time, 2))
        device_dic['r/s'].append(
            ((new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][
                ind]) / sys_start_time / _interval) if _interval else round(
                old_disk_stats_data['rd_ios'][ind] / sys_start_time, 2))
        device_dic['w/s'].append(
            ((new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][
                ind]) / sys_start_time / _interval) if _interval else round(
                old_disk_stats_data['wr_ios'][ind] / sys_start_time, 2))
        device_dic['rrqm/s'].append(
            ((new_disk_stats_data['rd_merges'][ind] - old_disk_stats_data['rd_merges'][
                ind]) / sys_start_time / _interval) if _interval else round(
                old_disk_stats_data['rd_merges'][ind] / sys_start_time, 2))
        device_dic['wrqm/s'].append(
            ((new_disk_stats_data['wr_merges'][ind] - old_disk_stats_data['wr_merges'][
                ind]) / sys_start_time / _interval) if _interval else round(
                old_disk_stats_data['wr_merges'][ind] / sys_start_time, 2))
        device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')].append(
           round((((new_disk_stats_data['rd_sectors'][ind] - old_disk_stats_data['rd_sectors'][
                ind]) / sys_start_time / _interval) if _interval else old_disk_stats_data['rd_sectors'][ind]) / sys_start_time * (512 / 1024), 2))
        device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')].append(round(
            (((new_disk_stats_data['wr_sectors'][ind] - old_disk_stats_data['wr_sectors'][
                ind]) /sys_start_time / _interval) if _interval else old_disk_stats_data['wr_sectors'][ind]) / sys_start_time * (512 / 1024), 2))
        device_dic[('kB_read', 'MB_read')].append(
            (device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')][ind] * sys_start_time) if _interval else
            device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')][ind])
        device_dic[('kB_wrtn', 'MB_wrtn')].append(
            (device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')][ind] * sys_start_time) if _interval else
            device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')][ind])
        device_dic['avgrq-sz'].append(
            round(((new_disk_stats_data['rd_sectors'][ind] - old_disk_stats_data['rd_sectors'][ind]) +
                   (new_disk_stats_data['wr_sectors'][ind] - old_disk_stats_data['wr_sectors'][ind])) /
                  ((new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind]) +
                   (new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind])), 2)
            if round(((new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind]) +
                      (new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind])), 2)
            else 0)
        device_dic['avgqu-sz'].append(round(
            ((new_disk_stats_data['time_in_queue'][ind] - old_disk_stats_data['time_in_queue'][
                ind]) / sys_start_time / _interval) if _interval else old_disk_stats_data['time_in_queue'][ind] / sys_start_time, 2))
        device_dic['await'].append(round(
            (new_disk_stats_data['rd_ticks'][ind] - old_disk_stats_data['rd_ticks'][ind] +
             new_disk_stats_data['wr_ticks'][ind] - old_disk_stats_data['wr_ticks'][ind]) /
            (new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind] +
             new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind]), 2) if round(
            (new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind] +
             new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind]), 2) else 0)
        device_dic['r_await'].append(
            round((new_disk_stats_data['rd_ticks'][ind] - old_disk_stats_data['rd_ticks'][ind]) / (
                    new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind]), 2) if
            round(new_disk_stats_data['rd_ios'][ind] - old_disk_stats_data['rd_ios'][ind], 2) else 0)
        device_dic['w_await'].append(
            round((new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ticks'][ind]) / (
                    new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind]), 2) if
            round(new_disk_stats_data['wr_ios'][ind] - old_disk_stats_data['wr_ios'][ind], 2) else 0)
        device_dic['%util'].append(
            round((new_disk_stats_data['io_ticks'][ind] - old_disk_stats_data['io_ticks'][ind]) / sys_start_time,
                  2))
        device_dic['svctm'].append(
            round(device_dic['%util'][ind] / device_dic['tps'][ind], 2) if device_dic['tps'][ind] else 0)
        # else:
        #     # device_dic['tps'].append(
        #     #     )
        #     # device_dic['r/s'].append()
        #     device_dic['w/s'].append()
        #     device_dic['rrqm/s'].append()
        #     device_dic['wrqm/s'].append()
        #     device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')].append(
        #         round((() * (512 / 1024) / sys_start_time), 2))
        #     device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')].append(
        #         round(((old_disk_stats_data['wr_sectors'][ind]) * (512 / 1024) / sys_start_time), 2))
        #     device_dic[('kB_read', 'MB_read')].append(
        #         round(device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')][ind] * sys_start_time, 2))
        #     device_dic[('kB_wrtn', 'MB_wrtn')].append(
        #         round(device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')][ind] * sys_start_time, 2))
        #     device_dic['avgrq-sz'].append(
        #         round((old_disk_stats_data['rd_sectors'][ind] + old_disk_stats_data['wr_sectors'][ind]) /
        #               (old_disk_stats_data['rd_ios'][ind] + old_disk_stats_data['wr_ios'][ind]) / sys_start_time, 2) if round(
        #             (old_disk_stats_data['rd_ios'][ind] + old_disk_stats_data['wr_ios'][ind]), 2) else 0)
        #     device_dic['avgqu-sz'].append(round(old_disk_stats_data['time_in_queue'][ind] / sys_start_time, 2))
        #     device_dic['await'].append(round(
        #         (old_disk_stats_data['rd_ticks'][ind] + old_disk_stats_data['wr_ticks'][ind]) / (
        #                 old_disk_stats_data['rd_ios'][ind] + old_disk_stats_data['wr_ios'][ind]), 2) if round(
        #         (old_disk_stats_data['rd_ios'][ind] + old_disk_stats_data['wr_ios'][ind]), 2) else 0)
        #     device_dic['r_await'].append(
        #         round(old_disk_stats_data['rd_ticks'][ind] / old_disk_stats_data['rd_ios'][ind], 2) if
        #         old_disk_stats_data['rd_ios'][ind] else 0)
        #     device_dic['w_await'].append(
        #         round(old_disk_stats_data['wr_ticks'][ind] / old_disk_stats_data['wr_ios'][ind], 2) if
        #         old_disk_stats_data['wr_ios'][ind] else 0)
        #     device_dic['%util'].append(round(old_disk_stats_data['io_ticks'][ind] / sys_start_time, 2))
        #     device_dic['svctm'].append(
        #         round(device_dic['%util'][ind] / device_dic['tps'][ind], 2) if device_dic['tps'][ind] else 0)
    # pprint(f"old: {old_disk_stats_data}")
    # pprint(f"new: {new_disk_stats_data}")
    # print(f"tps: {device_dic['tps']}")
    # print(new_disk_stats_data['rd_ios'][0] - old_disk_stats_data['rd_ios'][0])
    # print(f"r/s: {device_dic['r/s']}")
    # print(f"w/s: {device_dic['w/s']}")
    # print(f"rrqm/s: {device_dic['rrqm/s']}")
    # print(f"wrqm/s: {device_dic['wrqm/s']}")
    # print(f"('kB_read/s','MB_read/s', 'rkB/s'): {device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')]}")
    # print(f"('kB_wrtn/s','MB_wrtn/s', 'wkB/s'): {device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')]}")
    # print(f"('kB_read','MB_read'): {device_dic[('kB_read', 'MB_read')]}")
    # print(f"('kB_wrtn', 'MB_wrtn'): {device_dic[('kB_wrtn', 'MB_wrtn')]}")
    # print(f"avgrq-sz : {device_dic['avgrq-sz']}")
    # print(f"await: {device_dic['await']}")
    # print(f"r_await: {device_dic['r_await']}")
    # print(f"w_await: {device_dic['w_await']}")
    # print(f"%util: {device_dic['%util']}")
    return device_dic


def avg_cpu_data() -> dict:
    all_data = 0
    avg_cpu_dic = {}
    for val in stat_targets().values():
        all_data += float(val[0])
    for key, value in stat_targets().items():
        avg_cpu_dic[key] = round(float(value[0]) / all_data * 100, 2)
    return avg_cpu_dic


def avg_cpu_output():
    avg_cpu = avg_cpu_data()
    print("avg-cpu:  %user  %nice  %system  %iowait  %steal  %idle")
    print('        %s'    '%s'     '%s'    '%s'    '%s'    '%s' % (str(avg_cpu['user']).rjust(7, ' '),
                                                                   str(avg_cpu['nice']).rjust(7, ' '),
                                                                   str(avg_cpu['system']).rjust(7, ' '),
                                                                   str(avg_cpu['iowait']).rjust(7, ' '),
                                                                   str(avg_cpu['steal']).rjust(7, ' '),
                                                                   str(avg_cpu['idle']).rjust(7, ' ')))


def device_output(x, m, device, seconds):
    device_dic = device_data(int(seconds))

    if m:
        if x:
            print('\n')
            print(
                "Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util")
            if device:
                ind = device_dic['Device'].index(device)
                print('%s         %s   %s     %s     %s    %s    %s %s %s   %s   %s %s  %s  %s' % (
                device_dic['Device'][ind],
                device_dic['rrqm/s'][ind],
                device_dic['wrqm/s'][ind],
                device_dic['r/s'][ind],
                device_dic['w/s'][ind],
                round(device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')][ind] / 1024, 2),
                round(device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')][ind] / 1024, 2),
                device_dic['avgrq-sz'][ind],
                device_dic['avgqu-sz'][ind],
                device_dic['await'][ind],
                device_dic['r_await'][ind],
                device_dic['w_await'][ind],
                device_dic['svctm'][ind],
                device_dic['%util'][ind])
                      )
            for ind, val in enumerate(device_dic['Device']):
                if val.startswith(('sda', 'dm')):
                    print("%s         %s   %s     %s     %s    %s    %s %s %s   %s   %s %s  %s  %s"
                          % (device_dic['Device'][ind],
                             device_dic['rrqm/s'][ind],
                             device_dic['wrqm/s'][ind],
                             device_dic['r/s'][ind],
                             device_dic['w/s'][ind],
                             round(device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')][ind] / 1024, 2),
                             round(device_dic[('kB_wrtn/s', 'MB_wrtn/s', 'wkB/s')][ind] / 1024, 2),
                             device_dic['avgrq-sz'][ind],
                             device_dic['avgqu-sz'][ind],
                             device_dic['await'][ind],
                             device_dic['r_await'][ind],
                             device_dic['w_await'][ind],
                             device_dic['svctm'][ind],
                             device_dic['%util'][ind]))
                    # print(device_dic['avgqu-sz'][ind])
                    # print(device_dic['wrqm/s'])
                    # print(device_dic[('kB_read/s', 'MB_read/s', 'rkB/s')])
                    # print(device_dic['avgrq-sz'])
                    print(device_dic['avgqu-sz'])
        else:
            print("Device:            tps    MB_read/s    MB_wrtn/s    MB_read    MB_wrtn")
    else:
        if x:
            print(
                "Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util")
        else:
            print("Device:            tps    kB_read/s    kB_wrtn/s    kB_read    kB_wrtn")


def format_out_put(x: bool, m: bool, seconds, device: str):
    device_output(x, m, device, seconds)


if __name__ == '__main__':
    args = handle_args()
    interval = args['seconds']  # 采样周期
    # print(device_data(interval))
    # print(stat_targets())
    # print(avg_cpu_data())
    format_out_put(args['x'], args['m'], args['seconds'], args['device'])
    # sys_time()
    # time.sleep(interval)
    # output_values(interval)
    # pprint(diskstats_targets())
