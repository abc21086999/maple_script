import win32gui
import win32con


class WindowsObject:

    def __init__(self, hwnd: int):
        self.__hwnd = hwnd

    def _rect(self):
        l, t, r, b = win32gui.GetWindowRect(self.__hwnd)
        return l, t, r, b

    @property
    def left(self):
        return self._rect()[0]

    @property
    def top(self):
        return self._rect()[1]

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