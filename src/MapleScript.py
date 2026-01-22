import time
import PIL.Image
import threading
from src.utils.xiao_controller import XiaoController
from pathlib import Path
from src.utils.config_loader import YamlLoader
from src.utils.settings_manager import SettingsManager
from src.utils.windows_object import WindowsObject
from abc import ABC, abstractmethod
from src.utils.maple_vision import MapleVision


class MapleScript(ABC):

    def __init__(self, controller=None, log_callback=None):
        self.maple = WindowsObject.find_maple("MapleStoryClassTW")
        self.yaml_loader = YamlLoader()
        self.settings = SettingsManager()
        self.__vision = MapleVision(self.maple)
        self.__keyboard = controller
        self.__mouse = controller

        # 執行緒控制與 Log 回調
        self.__log_callback = log_callback
        # 使用 Event 作為停止信號，預設為 False (未停止)
        # 當 set() 被呼叫變成 True 時，代表要停止了
        self.__stop_event = threading.Event()

    def stop(self):
        """
        發送停止信號，所有正在運行的迴圈應該在檢測到此信號後退出
        """
        self.__stop_event.set()

    def should_continue(self) -> bool:
        """
        檢查是否應該繼續執行 (沒有收到停止信號)
        :return: True if running, False if stopped
        """
        return not self.__stop_event.is_set()

    def sleep(self, duration: float) -> bool:
        """
        可被中斷的睡眠。
        使用 Event.wait，如果收到停止信號會立刻醒來，不用等到時間結束。
        :param duration: 睡眠秒數
        :return: True 如果是被停止信號叫醒的, False 如果是睡飽了自然醒的
        """
        # wait 回傳 True 代表 flag 被 set 了 (也就是收到停止信號)
        # wait 回傳 False 代表 timeout 了 (也就是睡飽了)
        return self.__stop_event.wait(timeout=duration)

    def log(self, message: str):
        """
        統一的 Log 輸出，同時印在 Terminal 並傳送給 GUI (如果有的話)
        """
        formatted_msg = f"[{time.strftime('%H:%M:%S')}] {message}"
        print(formatted_msg)
        if self.__log_callback:
            self.__log_callback(formatted_msg)

    def invoke_menu(self) -> None:
        """
        打開總覽界面
        :return:
        """
        # 打開總攬界面
        self.press_and_wait("esc")
        # 確保有打開
        while self.should_continue() and not self.is_on_screen(self.yaml_loader.menu["menu_market_icon"]):
            self.sleep(0.5)
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
                self.sleep(0.2)

                self.click()
                self.sleep(0.2)
            case None:
                pass

    def replay_script(self, recorded_events: list[list | tuple]):
        """
        重播已經錄製的腳本
        :param recorded_events: 腳本list，元素可以是 tuple 或 list (e.g. [action, key, time])
        """
        start_replay_time = time.time()
        for action, key_str, event_time in recorded_events:
            if not self.should_continue():
                break

            if not self.is_maple_focus():
                self.log("楓之谷不在前景，中止重播腳本")
                self.__keyboard.release_all()
                break

            target_time = start_replay_time + event_time
            sleep_duration = target_time - time.time()
            if sleep_duration > 0:
                if self.sleep(sleep_duration): # 如果被中斷就停止
                    break

            if action == 'press':
                self.key_down(key_str)
            elif action == 'release':
                self.key_up(key_str)

        self.log("腳本重播完畢")

    def press(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.press_key(key)
        else:
            self.log(f'沒鍵盤')

    def press_and_wait(self, key: str | list[str], wait_time: float | int = 0.3):
        if not self.should_continue():
            return

        if isinstance(key, str):
            self.press(key)
            self.sleep(wait_time)
        elif isinstance(key, list):
            for k in key:
                if not self.should_continue():
                    break
                self.press(k)
                self.sleep(wait_time)

    def move(self, location: tuple) -> None:
        if self.__mouse is not None:
            self.__mouse.send_mouse_location(location)
        else:
            self.log(f'沒滑鼠')

    def click(self) -> None:
        if self.__mouse is not None:
            self.__mouse.click()
        else:
            self.log(f'沒滑鼠')

    def key_down(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.key_down(key)
            self.sleep(0.1)
        else:
            self.log(f'沒鍵盤')

    def key_up(self, key: str) -> None:
        if self.__keyboard is not None:
            self.__keyboard.key_up(key)
            self.sleep(0.1)
        else:
            self.log(f'沒鍵盤')

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
