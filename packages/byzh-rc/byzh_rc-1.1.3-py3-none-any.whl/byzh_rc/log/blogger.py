import threading
import time
import atexit

from ..drawer.terminal import BColor

COLOR_DICT = {
    "black": BColor.BLACK,
    "red": BColor.RED,
    "green": BColor.GREEN,
    "yellow": BColor.YELLOW,
    "blue": BColor.BLUE,
    "purple": BColor.PURPLE,
    "cyan": BColor.CYAN,
    "white": BColor.WHITE
}

class BLogger:
    def __init__(self, file=None, ifTime=False, color='white'):
        '''
        :param file: 日志保存路径
        :param ifTime: 是否输出时间
        '''
        self.file = file
        self.ifTime = ifTime

        assert color in COLOR_DICT, f"color参数错误，请输入{list(COLOR_DICT.keys())}"
        self.color = color

        self.f = None
        if self.file:
            self.f = open(self.file, "a", encoding="utf-8")

    def setFile(self, file, ifTime=False):
        if self.f:
            self.f.close()
        self.file = file
        self.ifTime = ifTime
        self.f = open(self.file, "a", encoding="utf-8")

    def clearFile(self):
        assert self.f is not None, "请先调用setFile方法"
        self.f.close()
        self.f = open(self.file, 'w', encoding="utf-8")

    def closeFile(self):
        if self.f:
            self.f.close()
            self.f = None

    def toCmd(self, string, color=None):
        # 检查color是否在字典中
        if color is None:
            print(COLOR_DICT.get(self.color) + string + BColor.RESET)
        else:
            assert color in COLOR_DICT, f"color参数错误，请输入{COLOR_DICT.keys()}"
            print(COLOR_DICT.get(color) + string + BColor.RESET)

    def toFile(self, string, ifTime=None):
        assert self.f is not None, "请先调用setFile方法"
        if ifTime == True:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())
            self.f.write(t)
        elif ifTime == False:
            pass
        elif self.ifTime:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())
            self.f.write(t)
        self.f.write(string)
        self.f.write("\n")
        self.f.flush()

    def toBoth(self, string, color=None):
        self.toFile(string)
        self.toCmd(string, color)
