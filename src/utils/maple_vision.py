import numpy as np
import cv2
import pyautogui
import PIL.Image
from pathlib import Path
import pyscreeze


class MapleVision:

    def __init__(self, maple):
        self.maple = maple
        self.mini_map_area = None
        self.other_player_color = [253, 45, 118]
        self.my_character_color = [239, 240, 12]
        self.mini_map_rectangle_color = [228, 228, 228]

    @property
    def maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple
        """
        return self.maple.left, self.maple.top, self.maple.width, self.maple.height

    @property
    def maple_skill_area(self):
        # 只要看右下角就好
        left, top, width, height = self.maple_full_screen_area
        return left+ width // 2, top + height // 2, width // 2, height // 2

    @property
    def maple_mini_map_area(self):
        """
        回傳小地圖位置，
        結果會被快取，只計算一次。
        """
        maple_x, maple_y, maple_w, maple_h = self.maple_full_screen_area
        mini_map_x, mini_map_y, mini_map_w, mini_map_h = self.get_mini_map_area()
        return maple_x + mini_map_x, maple_y + mini_map_y, mini_map_w, mini_map_h

    def get_full_screen_screenshot(self):
        return pyautogui.screenshot(region=self.maple_full_screen_area, allScreens=True)

    def get_skill_area_screenshot(self):
        return pyautogui.screenshot(region=self.maple_skill_area, allScreens=True)

    def get_mini_map_area_screenshot(self):
        return pyautogui.screenshot(region=self.maple_mini_map_area, allScreens=True)

    def get_mini_map_area(self):
        """
        計算小地圖在楓之谷視窗的相對位置
        :return: 小地圖在楓之谷視窗的相對位置
        """
        if self.mini_map_area is not None:
            return self.mini_map_area

        # 1. 鎖定搜尋範圍：只看視窗左上角 1/4 區域，提升效能
        full_x, full_y, full_w, full_h = self.maple_full_screen_area
        roi_w, roi_h = full_w // 6, full_h // 3

        # 截圖 (RGB 模式)
        img = pyautogui.screenshot(region=(full_x, full_y, roi_w, roi_h), allScreens=True)
        img_np = np.array(img)

        # 2. 設定目標顏色 (直接瞄準 228, 228, 228)
        lower_bound = np.array(self.mini_map_rectangle_color)
        upper_bound = np.array(self.mini_map_rectangle_color)

        # 3. 製作遮罩 (Mask)
        mask = cv2.inRange(img_np, lower_bound, upper_bound)

        # 4. 尋找輪廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            max_area = 0
            best_rect = None

            for cnt in contours:
                # 取得外接矩形
                x, y, w, h = cv2.boundingRect(cnt)

                # 過濾太小的雜訊 (例如寬度小於 50 的文字)
                if w < 50 or h < 50:
                    continue

                area = w * h
                if area > max_area:
                    max_area = area
                    best_rect = (x, y, w, h)

            # 回傳絕對座標
            if best_rect:
                rect_x, rect_y, rect_w, rect_h = best_rect
                # 加上視窗原本的起始座標
                self.mini_map_area = rect_x, rect_y, rect_w, rect_h
                return self.mini_map_area

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。 (NumPy 優化版)
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        # 1. 擷取小地圖畫面 (傳回的是 PIL Image, RGB 模式)
        minimap_img = self.get_mini_map_area_screenshot()

        # 2. 將圖片轉為 NumPy 陣列 (Height, Width, 3)
        img_np = np.array(minimap_img)

        # 3. 定義目標顏色 (R, G, B) - 黃點
        target_color = np.array(self.my_character_color)

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
        width = img_np.shape[1]  # shape is (Height, Width, Channels)
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
        minimap_img = self.get_mini_map_area_screenshot()
        img_np = np.array(minimap_img)

        # 2. 定義目標顏色 (R, G, B) - 玩家紅點 (253, 45, 118)
        target_color = np.array(self.other_player_color)

        # 3. 計算色差並建立遮罩 (符合顏色為 255, 不符合為 0)
        diff_matrix = np.sum(np.abs(img_np - target_color), axis=2)
        mask = (diff_matrix < (color_tolerance * 3)).astype(np.uint8) * 255

        # 4. 使用 3x3 Kernel 進行腐蝕 (Erosion)
        # 這會要求紅點必須至少是一個 3x3 的實心區塊
        kernel = np.ones((3, 3), np.uint8)
        eroded_mask = cv2.erode(mask, kernel, iterations=1)

        # 5. 如果腐蝕後還有殘留像素，代表地圖上有符合大小的紅點
        return cv2.countNonZero(eroded_mask) > 0

    def is_on_screen(self, pic: PIL.Image.Image | str | Path, img) -> bool:
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

    def find_image_location(self, pic_for_search: str | PIL.Image.Image | Path) -> tuple[int, int] | None:
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

                return dx, dy

            # 如果沒辨識到東西就不做任何事情
            else:
                print(f'畫面中找不到{pic_for_search}')

        except pyautogui.ImageNotFoundException:
            # 如果沒辨識到東西就不做任何事情
            print(f'畫面中找不到{pic_for_search}')