import time
import pyautogui
import pyscreeze
import PIL.Image
import numpy as np
import cv2
from src.XiaoController import XiaoController
from pathlib import Path
from src.ConfigLoader import YamlLoader
from src.WindowsObject import WindowsObject
from abc import ABC, abstractmethod


class MapleScript(ABC):

    def __init__(self, controller=None):
        self.maple = WindowsObject.find_maple("MapleStoryClassTW")
        self.yaml_loader = YamlLoader()
        self.__cur_path = Path(__file__).resolve().parent.parent
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

    def get_photo_path(self, pic_name: str) -> Path:
        """
        回傳圖片的路徑
        :param pic_name: 圖片的檔案名稱
        :return: Path
        """
        return self.__cur_path / "photos" / pic_name

    def is_maple_focus(self) -> bool:
        """
        根據楓之谷在不在前景決定回傳的bool值
        :return: bool
        """
        return self.maple.is_active

    @property
    def maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple
        """
        return self.maple.left, self.maple.top, self.maple.width, self.maple.height

    def get_full_screen_screenshot(self):
        return pyautogui.screenshot(region=self.maple_full_screen_area, allScreens=True)

    @property
    def maple_skill_area(self):
        # 只要看右下角就好
        left, top, width, height = self.maple_full_screen_area
        return left+ width // 2, top + height // 2, width // 2, height // 2

    @property
    def maple_mini_map_area(self):
        left, top, _, _ = self.maple_full_screen_area
        
        minimap_config = self.yaml_loader.ui_offsets.get('minimap', {})
        # 如果設定檔讀取失敗，使用預設值以防崩潰
        offset_x = minimap_config.get('x', 15)
        offset_y = minimap_config.get('y', 99)
        width = minimap_config.get('width', 182)
        height = minimap_config.get('height', 71)
        
        mini_map_region = left + offset_x, top + offset_y, width, height
        return mini_map_region

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。 (NumPy 優化版)
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        # 1. 擷取小地圖畫面 (傳回的是 PIL Image, RGB 模式)
        minimap_img = pyautogui.screenshot(region=self.maple_mini_map_area, allScreens=True)
        
        # 2. 將圖片轉為 NumPy 陣列 (Height, Width, 3)
        img_np = np.array(minimap_img)
        
        # 3. 定義目標顏色 (R, G, B) - 黃點
        target_color = np.array([239, 240, 12])
        
        # 4. 計算整張圖每個像素與目標顏色的差異 (向量化運算)
        # axis=2 表示沿著顏色通道 (R,G,B) 計算絕對差值的總和
        # 這裡會產生一個 (Height, Width) 的二維陣列
        diff_matrix = np.sum(np.abs(img_np - target_color), axis=2)
        
        # 5. 篩選符合容忍度的像素 (Boolean Mask)
        mask = diff_matrix < (color_tolerance * 3)
        
        # 6. 找出所有符合條件的座標 (y, x)
        # np.where 回傳的是 (row_indices, col_indices) -> (y座標陣列, x座標陣列)
        _, x_coords = np.where(mask)
        
        # 7. 如果沒找到任何匹配的像素
        if x_coords.size == 0:
            return "not_found"

        # 8. 計算平均 X 座標
        avg_x = np.mean(x_coords)
        
        # 9. 判斷位置 (比較平均 X 與圖片中心點)
        width = img_np.shape[1] # shape is (Height, Width, Channels)
        midpoint_x = width / 2

        if avg_x < midpoint_x:
            return "left"
        else:
            return "right"

    def has_other_players(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有其他玩家（紅點）。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        # 1. 擷取小地圖畫面
        minimap_img = pyautogui.screenshot(region=self.maple_mini_map_area, allScreens=True)
        img_np = np.array(minimap_img)

        # 2. 定義目標顏色 (R, G, B) - 玩家紅點 (253, 45, 118)
        target_color = np.array([253, 45, 118])

        # 3. 計算色差並建立遮罩 (符合顏色為 255, 不符合為 0)
        diff_matrix = np.sum(np.abs(img_np - target_color), axis=2)
        mask = (diff_matrix < (color_tolerance * 3)).astype(np.uint8) * 255

        # 4. 使用 3x3 Kernel 進行腐蝕 (Erosion)
        # 這會要求紅點必須至少是一個 3x3 的實心區塊
        kernel = np.ones((3, 3), np.uint8)
        eroded_mask = cv2.erode(mask, kernel, iterations=1)

        # 5. 如果腐蝕後還有殘留像素，代表地圖上有符合大小的紅點
        return cv2.countNonZero(eroded_mask) > 0

    def get_skill_area_screenshot(self):
        return pyautogui.screenshot(region=self.maple_skill_area, allScreens=True)

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

            # 校正滑鼠座標至虛擬螢幕座標系
            offset_x, offset_y = self.maple.screen_offset
            current_mouse_x -= offset_x
            current_mouse_y -= offset_y

            # 辨識遊戲截圖內有沒有我們要的東西
            # 改用截圖後 locate 避免 allScreens 參數錯誤
            screenshot = self.get_full_screen_screenshot()
            box = pyautogui.locate(pic, screenshot, confidence=0.9)

            # 如果有辨識到東西
            if box is not None:
                box_left, box_top, box_width, box_height = box

                # 計算目標中心點 (相對於虛擬螢幕座標系)
                win_x, win_y, _, _ = self.maple_full_screen_area
                target_x = win_x + box_left + box_width / 2
                target_y = win_y + box_top + box_height / 2

                # 計算目前滑鼠的相對位置
                dx = int(target_x - current_mouse_x)
                dy = int(target_y - current_mouse_y)

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
            time.sleep(0.3)
            print(Maple.has_other_players())
        print(Maple.get_character_position())
