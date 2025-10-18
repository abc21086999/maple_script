import sys
import time
import pygetwindow as gw
import pyautogui
import pyscreeze
import PIL.Image
from XiaoController import XiaoController
from pathlib import Path


class MapleScript:

    def __init__(self, controller=None):
        self.maple = self._get_maple()
        self.maple_full_screen_area = self.__get_maple_full_screen_area()
        self.maple_skill_area = self.__get_maple_skill_area()
        self.maple_mini_map_area = self.__get_mini_map_area()
        self.__cur_path = Path(__file__).resolve().parent
        self.__keyboard = controller
        self.__mouse = controller

    @staticmethod
    def __get_window_area(window: gw.Win32Window):
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
        #TODO: 用其他package取代gw，因為gw完全是靠標題來辨識
        maplestory = gw.getWindowsWithTitle("Maplestory")
        # 在找不到的情況下，代表楓之谷沒開啟，直接結束腳本
        if not maplestory:
            print("找不到楓之谷的程式")
            sys.exit()
        # 如果回傳的視窗有兩個，代表有一個是遊戲本體，一個是聊天室，但是遊戲本體一定比聊天室還要大
        real_maple = max(maplestory, key=self.__get_window_area)
        if not real_maple.isActive:
            real_maple.activate()
        return real_maple

    def is_maple_focus(self) -> bool:
        """
        根據楓之谷在不在前景決定回傳的bool值
        :return: bool
        """
        return self.maple.isActive

    def __get_maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple
        """
        return self.maple.left, self.maple.top, self.maple.width, self.maple.height

    def get_full_screen_screenshot(self):
        return pyautogui.screenshot(region=self.maple_full_screen_area)

    def __get_maple_skill_area(self):
        # 只要看右下角就好
        left, top, width, height = self.maple_full_screen_area
        return left+ width // 2, top + height // 2, width // 2, height // 2

    def __get_mini_map_area(self):
        left, top, _, _ = self.maple_full_screen_area
        mini_map_region = left+15, top+99, 182, 71
        return mini_map_region

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        # 1. 擷取小地圖畫面
        minimap_img = pyautogui.screenshot(region=self.maple_mini_map_area)
        width, height = minimap_img.size
        target_color = (239, 240, 12)
        found_x_coords = []

        # 2. 遍歷像素 (為了效能，每隔3個像素檢查一次)
        for x in range(0, width, 3):
            for y in range(0, height, 3):
                pixel_color = minimap_img.getpixel((x, y))
                
                # 3. 比較顏色
                if sum(abs(pixel_color[i] - target_color[i]) for i in range(3)) < color_tolerance * 3:
                    found_x_coords.append(x)

        # 4. 如果沒找到任何匹配的像素
        if not found_x_coords:
            return "not_found"

        # 5. 計算平均X座標並判斷位置
        avg_x = sum(found_x_coords) / len(found_x_coords)
        midpoint_x = width / 2

        if avg_x < midpoint_x:
            return "left"
        else:
            return "right"

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
            current_mouse_x, current_mouse_y = pyautogui.position()

            # 辨識遊戲截圖內有沒有我們要的東西
            picture_location = pyautogui.locateCenterOnScreen(pic, region=self.maple_full_screen_area, confidence=0.9)

            # 如果有辨識到東西
            if picture_location is not None:
                # 計算目前滑鼠的相對位置
                dx = int(picture_location.x - current_mouse_x)
                dy = int(picture_location.y - current_mouse_y)

                # 移動過去
                self.move((dx, dy))
                time.sleep(0.1)

                # 點下
                self.click()
                time.sleep(0.3)

            # 如果沒辨識到東西就不做任何事情
            else:
                print(f'畫面中找不到{pic_for_search}')

        except pyautogui.ImageNotFoundException:
            # 如果沒辨識到東西就不做任何事情
            print(f'畫面中找不到{pic_for_search}')


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
        print(Maple.get_character_position())