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
        self._model = None
        self._vision = MapleVision(self.maple)
        self._keyboard = controller
        self._mouse = controller

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

    def cleanup(self):
        """
        清理資源，例如關閉視覺辨識物件
        """
        self._vision.release()

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
        return self._vision.get_full_screen_screenshot()

    def get_skill_area_screenshot(self):
        return self._vision.get_skill_area_screenshot()

    def get_mini_map_area_screenshot(self):
        return self._vision.get_mini_map_area_screenshot()

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。 (NumPy 優化版)
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        return self._vision.get_character_position(color_tolerance)

    def has_other_players(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有其他玩家（紅點）。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        return self._vision.has_other_players(color_tolerance)

    def has_rune(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有有沒有倫。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        return self._vision.has_rune(color_tolerance)

    def get_player_pos(self) -> tuple[int, int] | None:
        """
        獲取玩家在小地圖上的精確座標 (x, y)
        """
        return self._vision.get_player_pos()

    def get_rune_pos(self) -> tuple[int, int] | None:
        """
        獲取符文在小地圖上的精確座標 (x, y)
        """
        return self._vision.get_rune_pos()

    def up_jump(self):
        """
        模擬向上跳躍 (Alt -> Up + Alt)
        """
        if self.is_maple_focus():
            self.press("alt")
            self.sleep(0.1)
            self.key_down("up")
            self.press("alt")
            self.key_up("up")
            self.sleep(0.5)

    def down_jump(self):
        """
        模擬向下跳躍 (Down + Alt)
        """
        if self.is_maple_focus():
            self.key_down("down")
            self.press("alt")
            self.sleep(0.1)
            self.key_up("down")
            self.sleep(0.5)

    def move_to_point(self, target_x: int, target_y: int, threshold: int = 3):
        """
        導航至小地圖上的特定座標
        """
        self.log(f"開始導航至目標座標")
        
        current_dir = None  # 紀錄硬體目前的物理狀態 (None, "left", "right")

        # 定義一個內部的同步函數，只在狀態改變時發送指令
        def sync_hardware(new_dir):
            nonlocal current_dir
            if new_dir == current_dir:
                return # 狀態沒變，不發指令，不浪費時間
            
            # 狀態改變了，先確保之前的方向鍵放開
            if current_dir:
                self.key_up(current_dir)
            
            # 再按下新的方向鍵
            if new_dir:
                self.key_down(new_dir)
            
            current_dir = new_dir # 更新記憶狀態

        try:
            while self.should_continue() and self.is_maple_focus():
                curr = self.get_player_pos()
                if not curr:
                    self.log("找不到玩家位置，等待中...")
                    self.sleep(0.5)
                    continue
                
                cx, cy = curr
                dx = target_x - cx
                dy = target_y - cy
                
                # 判斷是否抵達目標 (水平與垂直都到位)
                if abs(dx) <= threshold and abs(dy) <= threshold:
                    self.log("已抵達目標點")
                    break
                    
                # --- 決定理想的方向 (拆解寫法，一目瞭然) ---
                if dx > threshold:
                    target_dir = "right"
                elif dx < -threshold:
                    target_dir = "left"
                else:
                    target_dir = None
                
                # --- 同步硬體狀態 (只在方向改變時發指令) ---
                sync_hardware(target_dir)
                
                # 處理垂直移動 (這部分會與水平同時進行)
                # 只有在接近目標 X 座標時才處理 Y，避免因為地形跳過頭
                if abs(dx) <= threshold * 3:
                    if dy < -threshold: # 目標在上方
                        self.up_jump()
                    elif dy > threshold: # 目標在下方
                        self.down_jump()
                
                # 迴圈頻率穩定維持 20fps (0.05s)
                # 因為 sync_hardware 絕大部分時間會 return，所以迴圈反應極快
                self.sleep(0.05)
                
        finally:
            # 確保退出時同步為停止狀態，並釋放所有可能的按鍵
            sync_hardware(None)
            if self._keyboard:
                self._keyboard.release_all()

    def is_on_screen(self, pic: PIL.Image.Image | str | Path, img=None) -> bool:
        """
        辨識想要找的東西在不在畫面上
        :param pic: 想要辨識的圖片
        :param img: 一張截圖，沒有傳入就會自動擷取一張
        :return: bool
        """
        return self._vision.is_on_screen(pic=pic, img=img)

    def find_and_click_image(self, pic_for_search: str | PIL.Image.Image | Path) -> None:
        """
        用於辨識按鈕之後移動
        :param pic_for_search: 要辨識的圖片
        :return: None
        """
        match self._vision.find_image_location(pic_for_search):
            case (dx, dy):
                self.move((dx, dy))
                self.sleep(0.2)

                self.click()
                self.sleep(0.2)
            case None:
                pass

    def replay_script(self, recorded_events: list[dict]):
        """
        重播已經錄製的腳本
        :param recorded_events: 腳本list，元素是字典 (e.g. {'action': 'key_down', 'key': 'a', 'time': 0.1})
        """
        start_replay_time = time.time()
        for event in recorded_events:
            if not self.should_continue():
                self._keyboard.release_all()
                break

            if not self.is_maple_focus():
                self.log("楓之谷不在前景，中止重播腳本")
                self._keyboard.release_all()
                break

            action = event.get('action')
            key_str = event.get('key')
            event_time = event.get('time')

            target_time = start_replay_time + event_time
            sleep_duration = target_time - time.time()
            if sleep_duration > 0:
                if self.sleep(sleep_duration): # 如果被中斷就停止
                    break

            if action == 'key_down':
                self.key_down(key_str)
            elif action == 'key_up':
                self.key_up(key_str)

        self.log("腳本重播完畢")

    def press(self, key: str) -> None:
        if self._keyboard is not None:
            self._keyboard.press_key(key)
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
        if self._mouse is not None:
            self._mouse.send_mouse_location(location)
        else:
            self.log(f'沒滑鼠')

    def click(self) -> None:
        if self._mouse is not None:
            self._mouse.click()
        else:
            self.log(f'沒滑鼠')

    def key_down(self, key: str) -> None:
        if self._keyboard is not None:
            self._keyboard.key_down(key)
            self.sleep(0.1)
        else:
            self.log(f'沒鍵盤')

    def key_up(self, key: str) -> None:
        if self._keyboard is not None:
            self._keyboard.key_up(key)
            self.sleep(0.1)
        else:
            self.log(f'沒鍵盤')

    def scroll_up(self) -> None:
        if self._mouse is not None:
            self._mouse.scroll_up()
        else:
            print(f'沒滑鼠')

    def scroll_down(self) -> None:
        if self._mouse is not None:
            self._mouse.scroll_down()
        else:
            print(f'沒滑鼠')

    @abstractmethod
    def start(self):
        pass



if __name__ == "__main__":
    from PySide6.QtCore import QCoreApplication

    # 由於序號的位置需要公司名稱和軟體名稱
    # 所以在這個檔案執行的時候要先初始化Qt框架然後做設定
    app = QCoreApplication([])
    app.setOrganizationName("MapleScriptTeam")
    app.setApplicationName("MapleScript")

    class DebugMaple(MapleScript):

        def start(self):
            pass

    with XiaoController() as Xiao:
        Maple = DebugMaple(Xiao)
        Maple.up_jump()