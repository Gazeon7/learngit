# encoding = "utf-8"
import sys


def juxing():
    lenth = int(sys.argv[1])
    width = int(sys.argv[2])
    if not isinstance(lenth, (int, float)) or not isinstance(width, (int, float)):
        raise ValueError
    if lenth < 0 or width < 0:
        raise ValueError(" it can't be minus")
    if lenth == 1:
        print('*\n' * width)
    elif width == 1:
        print("*" * lenth)
    elif width == 0 or lenth ==0:
        raise ValueError(" it can' be zero")
    else:
        for i in range(width):
            if i == 0 or i == width - 1:
                print('*' * lenth)
            else:
                print('*' + (lenth - 2) * ' ' + '*')


if __name__ == '__main__':
    juxing()
