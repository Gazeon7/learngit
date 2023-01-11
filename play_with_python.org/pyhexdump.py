import argparse
from io import SEEK_SET, SEEK_END

from typing import List

SIZE = 16


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str)
    parser.add_argument('-C', action='store_true')
    parser.add_argument('-s', type=int, required=False, default=0)
    parser.add_argument('-n', type=int, required=False, default=0)
    _args = vars(parser.parse_args())
    return _args


def read_file(file_path: str, s, n) -> bytes:
    """
    读取文件内容返回二进制格式
    :param file_path: 文件路径
    :param s: 偏移量
    :param n: 格式化字符数
    :return: 返回bytes对象
    """
    bytes_data = None
    with open(file_path, 'rb') as f:
        f.seek(0, SEEK_END)
        n = f.tell() if not n else n    # n默认值为文件字节大小
        # f.seek(0, SEEK_SET)
        f.seek(s, SEEK_SET)
        bytes_data = f.read(n)
    print(s, n)
    return bytes_data


def hexdump(_data, ascii_status=False):
    """
    hexdump处理
    :param _data:二进制数据
    :param ascii_status: 是否返回ASCII值
    :return: (偏移量，ASCII值， 字符) or (偏移量，ASCII值)
    """
    start = 0
    stop = 1 if ascii_status else 2
    for ind, val in enumerate(_data):
        ele = int.from_bytes(_data[start: stop], byteorder='little')
        if ascii_status:
            yield '{:08x}'.format(ind), '{:02x}'.format(ele), chr(ele) if 32 < ele < 126 else '.'
            start += 1
            stop += 1
        else:
            yield '{:07x}'.format(ind * 2), '{:02x}'.format(ele)
            start, stop = stop, stop + 2
        if not _data[start: stop]:
            break


def unpack_hexdump(_data, ascii_status=False):
    """
    解包hexdump处理过的数据
    :param _data: hexdump处理过的数据
    :param ascii_status: 是否需要ASCII值
    :return: 返回每个字节的偏移量、ASCII值、ASICC字符
    """
    s = []
    ascii_val = []
    ascii_char = []
    if ascii_status:
        for val in zip(_data):
            """解包存入对应列表"""
            for x, y, z in val:
                s.append(x)
                ascii_val.append(y)
                ascii_char.append(z)
        return s, ascii_val, ascii_char
    else:
        for val in zip(_data):
            # print(f"非-C情况解包：{val}")
            for x, y in val:
                # print(x,y)
                s.append(x)
                ascii_val.append(y)
        # print(s, ascii_val)
        return s, ascii_val

def format_unpacked_values_from_hexdump(_data, ascii_status=False) -> list:
    """
    格式化从unpack_hexdump解包的数据
    :param _data: 从unpack_hexdump解包的数据
    :return: 返回格式化后的字符串列表
    """
    val_temp = []
    val_list = []  # n行十六列
    val_str = ''
    res = []
    for ind, val in enumerate(_data):

        """将所有元素按一行十六列保存到二维列表val_list"""
        val_temp.append(val)
        if len(val_temp) == SIZE:
            val_list.append(val_temp)
            val_temp = []  # 重新初始化存放下一行
        if ind == len(data) - 1:
            """将不足十六列的剩余元素保存到val_list"""
            val_list.append(val_temp)

        """格式化输出"""
    # print(val_list)
    for ind, val in enumerate(val_list):
        for ele in val:
            # print(f"格式化输出：{ele}")
            if ascii_status:
                val_str += ele + ' '    # 把列表中的元素拼成字符串
                # print(f"val_str:{val_str}")
            else:
                val_str += ele
        res.append(val_str)
        val_str = ''  # 初始化字符串变量
    # print(res)
    return res


def get_offset(_data: list) -> list:
    """
    获取每行偏移量
    :param _data: 偏移量列表
    :return: 每行偏移量的列表
    """
    res = []
    for ind, off in enumerate(_data):
        if ind % SIZE == 0:
            res.append(off)
    # print(res)
    return res


def format_output(offect: list, ascii_value: List[str], count_bytes, ascii_status = False, ascii_char=None):
    """
    格式化输出
    :param offect: 偏移量
    :param ascii_value: ascii值
    :param count_bytes: 总字节数
    :param ascii_status: 是否获取ascii值
    :param ascii_char: ascii字符
    :return:
    """
    global out_put
    if ascii_char is None:
        ascii_char = []
    if ascii_status:
        for num in range(len(offect)):
            print(f"{offect[num]} {ascii_value[num].ljust(50, ' ')} |{ascii_char[num]}|")
        # print(ascii_value[0][:4])
        print('{:08x}'.format(count_bytes))

    else:
        ascii_value_data = ascii_value[0].split(' ')

        for num in range(len(offect)):
            # print(num)
            """控制行数"""
            temp = []
            for ind in range(len(ascii_value_data)):
                # print(ascii_value[])
                # print(f"val:{ascii_value[ind]}")
                temp.append(ascii_value_data[ind])
                # print(temp)
                # print(len(temp))
                if len(temp) % 8 == 0 and len(temp) != 0:
                    # print(temp)
                    out_put: str = f"{offect[num]} {' '.join(temp).zfill(4)}"
                    temp = []
            print(out_put)
        # print('\n')
        print('{:07x}'.format(count_bytes * 2))

def main(_data, ascii_status):
    hexdump_data = list(hexdump(_data, args['C']))
    if ascii_status:
        offset, ascii_value, ascii_char = unpack_hexdump(hexdump_data, args['C'])
        count_bytes = len(ascii_value)
        format_offset = get_offset(offset)
        format_ascii_value = format_unpacked_values_from_hexdump(ascii_value, args['C'])
        format_ascii_char = format_unpacked_values_from_hexdump(ascii_char)
        format_output(format_offset, format_ascii_value, count_bytes, ascii_status=args['C'], ascii_char=format_ascii_char)
    else:
        offset, ascii_value = unpack_hexdump(hexdump_data)
        count_bytes = len(ascii_value)
        format_offset = get_offset(offset)
        format_ascii_value = format_unpacked_values_from_hexdump(ascii_value)
        format_output(format_offset, format_ascii_value, count_bytes)

if __name__ == '__main__':
    args = handle_args()
    data = read_file(args['file_path'], args['s'], args['n'])
    # hexdump(data, True)
    hexdump_data = list(hexdump(data, True))    # 获取hexdump后的值    # -C
    # hexdump_data = list(hexdump(data))
    # print(f"hexdump:{list(hexdump_data)}")
    offset, ascii_value, ascii_char = unpack_hexdump(hexdump_data, True)  # -C
    # offset, ascii_value, ascii_char = unpack_hexdump(hexdump_data)  # -C
    # offset, ascii_value = unpack_hexdump(hexdump_data)
    # print(ascii_value)
    count_bytes = len(ascii_value)    # 获取字节长度
    # print(f"count_bytes:{count_bytes}")
    format_offset = get_offset(offset)
    # print(f"format_offect: {format_offset}")
    format_ascii_value = format_unpacked_values_from_hexdump(ascii_value, True)   # -C
    # format_ascii_value = format_unpacked_values_from_hexdump(ascii_value, True)
    format_ascii_char = format_unpacked_values_from_hexdump(ascii_char) # -C
    # print(format_offset)
    # print(format_ascii_value)
    # print(format_ascii_char)    # -C
    format_output(format_offset, format_ascii_value, count_bytes, ascii_status=True, ascii_char = format_ascii_char)   # -C
    # format_output(format_offset, format_ascii_value, count_bytes)
