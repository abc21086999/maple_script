import sys
import time
import pygetwindow as gw
import pyautogui
import random
import pyscreeze
import PIL.Image
from XiaoController import XiaoController
from pathlib import Path


class MapleScript:

    def __init__(self, controller=None):
        self.maple = self._get_maple()
        self.maple_full_screen_area = self._get_maple_full_screen_area()
        self.maple_skill_area = self._get_maple_skill_area()
        self.__cur_path = Path(__file__).resolve().parent
        self.__keyboard = controller
        self.__mouse = controller

    @staticmethod
    def _get_window_area(window: gw.Win32Window):
        """
        這是一個計算視窗面積的輔助函式，專門給 max() 的 key 使用。
        """
        return window.width * window.height

    def get_photo_path(self, pic_name: str) -> Path:
        """
        回傳圖片的路徑
        :param pic_name: 圖片的檔案名稱
        :return: Path
        """
        return self.__cur_path / "photos" / pic_name

    def _get_maple(self):
        """
        切換到楓之谷的程式
        :return: 楓之谷程式
        """
        maplestory = gw.getWindowsWithTitle("Maplestory")
        # 在找不到的情況下，代表楓之谷沒開啟，直接結束腳本
        if not maplestory:
            print("找不到楓之谷的程式")
            sys.exit()
        # 如果回傳的視窗有兩個，代表有一個是遊戲本體，一個是聊天室，但是遊戲本體一定比聊天室還要大
        real_maple = max(maplestory, key=self._get_window_area)
        if not real_maple.isActive:
            real_maple.activate()
        return real_maple

    def is_maple_focus(self) -> bool:
        """
        根據楓之谷在不在前景決定回傳的bool值
        :return: bool
        """
        return self.maple.isActive

    def _get_maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple
        """
        return self.maple.left, self.maple.top, self.maple.width, self.maple.height

    def get_full_screen_screenshot(self):
        return pyautogui.screenshot(region=self.maple_full_screen_area)

    def _get_maple_skill_area(self):
        # 只要看右下角就好
        left, top, width, height = self.maple_full_screen_area
        return left+ width // 2, top + height // 2, width // 2, height // 2

    def get_skill_area_screenshot(self):
        return pyautogui.screenshot(region=self.maple_skill_area)

    def is_on_screen(self, pic: PIL.Image.Image | str | Path, img=None) -> bool:
        """
        辨識想要找的東西在不在畫面上
        :param pic: 想要辨識的圖片
        :param img: 一張截圖，沒有傳入就會自動擷取一張
        :return: bool
        """
        # 處理各種路徑格式
        if isinstance(pic, str):
            pic = PIL.Image.open(pic)
        elif isinstance(pic, Path):
            pic = PIL.Image.open(str(pic))

        # 如果沒有傳入截圖，那就截一張圖
        if img is None:
            img = self.get_full_screen_screenshot()

        try:
            skill_location = next(pyautogui.locateAll(pic, img, confidence=0.96), None)
            return bool(skill_location)
        except pyscreeze.ImageNotFoundException:
            return False

    def find_and_click_image(self, pic_for_search: str | PIL.Image.Image | Path) -> None:
        """
        用於辨識按鈕之後移動
        :param pic_for_search: 要辨識的圖片
        :return: None
        """
        # 處理各種不同的路徑格式
        if isinstance(pic_for_search, str):
            pic = PIL.Image.open(pic_for_search)
        elif isinstance(pic_for_search, Path):
            pic = PIL.Image.open(str(pic_for_search))
        else:
            pic = pic_for_search

        try:
            # 取得目前滑鼠位置
            current_mouse_location = pyautogui.position()

            # 辨識遊戲截圖內有沒有我們要的東西
            picture_location = pyautogui.locateCenterOnScreen(pic, region=self.maple_full_screen_area, confidence=0.9)

            # 如果有辨識到東西
            if picture_location is not None:
                # 計算目前滑鼠的相對位置
                dx = int(picture_location.x - current_mouse_location[0])
                dy = int(picture_location.y - current_mouse_location[1])

                # 移動過去
                self.move((dx, dy))
                time.sleep(0.1)

                # 點下
                self.click()
                time.sleep(0.3)

            # 如果沒辨識到東西就不做任何事情
            else:
                print(f'畫面中找不到{pic}')

        except pyautogui.ImageNotFoundException:
            # 如果沒辨識到東西就不做任何事情
            print(f'畫面中找不到{pic}')


    def press(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.press_key(key)
        else:
            print(f'沒鍵盤')

    def press_and_wait(self, key: str | list[str], wait_time: float | int = 0.3):
        if isinstance(key, str):
            self.press(key)
            time.sleep(wait_time)
        elif isinstance(key, list):
            for k in key:
                self.press(k)
                time.sleep(wait_time)

    def move(self, location: tuple) -> None:
        if self.__mouse is not None:
            self.__mouse.send_mouse_location(location)
        else:
            print(f'沒滑鼠')

    def click(self) -> None:
        if self.__mouse is not None:
            self.__mouse.click()
        else:
            print(f'沒滑鼠')

    def key_down(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.key_down(key)
            time.sleep(0.1)
        else:
            print(f'沒鍵盤')

    def key_up(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.key_up(key)
            time.sleep(0.1)
        else:
            print(f'沒鍵盤')

    def scroll_up(self) -> None:
        if self.__mouse is not None:
            self.__mouse.scroll_up()
        else:
            print(f'沒滑鼠')

    def scroll_down(self) -> None:
        if self.__mouse is not None:
            self.__mouse.scroll_down()
        else:
            print(f'沒滑鼠')


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = MapleScript(Xiao)
