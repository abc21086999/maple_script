import time
import win32gui
import win32con
import win32api
import sys
from typing import Self


class WindowsObject:

    def __init__(self, hwnd: int):
        self.__hwnd = hwnd

    def _rect(self):
        l, t, r, b = win32gui.GetWindowRect(self.__hwnd)
        return l, t, r, b

    @property
    def screen_offset(self) -> tuple[int, int]:
        """
        回傳虛擬螢幕的左上角座標偏移量 (x, y)
        """
        screen_x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        screen_y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        return screen_x, screen_y

    @property
    def left(self):
        l, _, _, _ = self._rect()
        offset_x, _ = self.screen_offset
        return l - offset_x

    @property
    def top(self):
        _, t, _, _ = self._rect()
        _, offset_y = self.screen_offset
        return t - offset_y

    @property
    def width(self):
        l, _, r, _ = self._rect()
        return r - l

    @property
    def height(self):
        _, t, _, b = self._rect()
        return b - t

    @property
    def is_active(self) -> bool:
        """
        回傳楓之谷視窗是否在前景
        :return: bool
        """
        return win32gui.GetForegroundWindow() == self.__hwnd

    def activate(self):
        """
        將楓之谷視窗取消最小化並拉到前景
        """
        if win32gui.IsIconic(self.__hwnd):
            win32gui.ShowWindow(self.__hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.__hwnd)

    @property
    def size(self):
        """
        回傳視窗的大小
        :return:
        """
        return self.width * self.height

    @classmethod
    def find_maple(cls, class_name : str) -> Self:
        """
        根據傳入的視窗class name找到正確的楓之谷視窗
        :return:
        """
        hwnds = []
        def callback(hwnd, _):
            if win32gui.GetClassName(hwnd) == class_name:
                hwnds.append(hwnd)
        win32gui.EnumWindows(callback, None)

        # 在找不到的情況下，代表楓之谷沒開啟，直接結束腳本
        if not hwnds:
            print("找不到楓之谷的程式")
            input("輸入任意鍵繼續...")
            sys.exit()

        # 將找到的視窗都先建立成物件
        all_maple = [cls(h) for h in hwnds]

        # 一個一個拉到前景
        for maple in all_maple:
            maple.activate()

        # 比較視窗大小並回傳最大的那個
        real_maple = max(all_maple, key=lambda x:x.size)
        time.sleep(0.1)
        return real_maple

if __name__ == "__main__":
    Maple = WindowsObject.find_maple("MapleStoryClassTW")
    print(Maple.is_active)
    print(Maple.size)