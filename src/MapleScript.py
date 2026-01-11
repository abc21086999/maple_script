import time
import PIL.Image
from src.utils.xiao_controller import XiaoController
from pathlib import Path
from src.utils.config_loader import YamlLoader
from src.utils.windows_object import WindowsObject
from abc import ABC, abstractmethod
from src.utils.maple_vision import MapleVision


class MapleScript(ABC):

    def __init__(self, controller=None):
        self.maple = WindowsObject.find_maple("MapleStoryClassTW")
        self.yaml_loader = YamlLoader()
        self.__vision = MapleVision(self.maple)
        self.__keyboard = controller
        self.__mouse = controller

    def invoke_menu(self) -> None:
        """
        打開總攬界面
        :return:
        """
        # 打開總攬界面
        self.press_and_wait("esc")
        # 確保有打開
        while not self.is_on_screen(self.yaml_loader.menu["menu_market_icon"]):
            time.sleep(0.5)
            self.press_and_wait("esc")
        return None

    def is_maple_focus(self) -> bool:
        """
        根據楓之谷在不在前景決定回傳的bool值
        :return: bool
        """
        return self.maple.is_active

    def get_full_screen_screenshot(self):
        return self.__vision.get_full_screen_screenshot()

    def get_skill_area_screenshot(self):
        return self.__vision.get_skill_area_screenshot()

    def get_mini_map_area_screenshot(self):
        return self.__vision.get_mini_map_area_screenshot()

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。 (NumPy 優化版)
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        return self.__vision.get_character_position(color_tolerance)

    def has_other_players(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有其他玩家（紅點）。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        return self.__vision.has_other_players(color_tolerance)

    def has_rune(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有倫。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        return self.__vision.has_rune(color_tolerance)

    def is_on_screen(self, pic: PIL.Image.Image | str | Path, img=None) -> bool:
        """
        辨識想要找的東西在不在畫面上
        :param pic: 想要辨識的圖片
        :param img: 一張截圖，沒有傳入就會自動擷取一張
        :return: bool
        """
        return self.__vision.is_on_screen(pic=pic, img=img)

    def find_and_click_image(self, pic_for_search: str | PIL.Image.Image | Path) -> None:
        """
        用於辨識按鈕之後移動
        :param pic_for_search: 要辨識的圖片
        :return: None
        """
        match self.__vision.find_image_location(pic_for_search):
            case (dx, dy):
                self.move((dx, dy))
                time.sleep(0.2)

                self.click()
                time.sleep(0.2)
            case None:
                pass

    def replay_script(self, recorded_events: list[list | tuple]):
        """
        重播已經錄製的腳本
        :param recorded_events: 腳本list，元素可以是 tuple 或 list (e.g. [action, key, time])
        """
        start_replay_time = time.time()
        for action, key_str, event_time in recorded_events:
            if not self.is_maple_focus():
                print("楓之谷不在前景，中止重播腳本")
                self.__keyboard.release_all()
                break

            target_time = start_replay_time + event_time
            sleep_duration = target_time - time.time()
            if sleep_duration > 0:
                time.sleep(sleep_duration)

            if action == 'press':
                self.key_down(key_str)
            elif action == 'release':
                self.key_up(key_str)

        print("腳本重播完畢")

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

    @abstractmethod
    def start(self):
        pass



if __name__ == "__main__":
    class DebugMaple(MapleScript):

        def start(self):
            pass

    with XiaoController() as Xiao:
        Maple = DebugMaple(Xiao)
        while True:
            time.sleep(0.5)
            print(Maple.has_rune())
