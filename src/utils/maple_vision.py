import mss
import cv2
import numpy as np
import PIL.Image
from pathlib import Path
import win32api


class MapleVision:

    def __init__(self, maple):
        self.maple = maple
        self.sct = mss.mss()
        
        # 定義顏色 (BGR 格式)
        self.other_player_color = np.array([118, 45, 253])       # Pink Bean Red
        self.my_character_color = np.array([12, 240, 239])       # Character Yellow
        self.rune_color = np.array([255, 102, 221])              # Rune Purple
        self.mini_map_rectangle_color = np.array([228, 228, 228]) # Minimap Border Gray

        self.mini_map_area = None

    def __del__(self):
        self.release()

    def release(self):
        if hasattr(self, 'sct'):
            self.sct.close()
            del self.sct

    @property
    def maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple (left, top, width, height)
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

    def _capture(self, region):
        """
        使用 mss 截取指定區域並回傳 BGR 格式影像
        :param region: tuple (left, top, width, height)
        :return: BGR NumPy Array
        """
        left, top, width, height = region
        monitor = {
            "left": int(left),
            "top": int(top),
            "width": int(width),
            "height": int(height)
        }
        
        # mss grab returns a BGRA image
        sct_img = self.sct.grab(monitor)
        
        # Convert to numpy array
        img_np = np.array(sct_img)
        
        # Convert BGRA to BGR (OpenCV format)
        return cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

    def get_full_screen_screenshot(self):
        return self._capture(self.maple_full_screen_area)

    def get_skill_area_screenshot(self):
        return self._capture(self.maple_skill_area)

    def get_mini_map_area_screenshot(self):
        return self._capture(self.maple_mini_map_area)

    def get_mini_map_area(self):
        """
        計算小地圖在楓之谷視窗的相對位置
        :return: 小地圖在楓之谷視窗的相對位置
        """
        if self.mini_map_area is not None:
            return self.mini_map_area

        # 1. 鎖定搜尋範圍：只看視窗左上角 1/4 區域
        full_x, full_y, full_w, full_h = self.maple_full_screen_area
        roi_w, roi_h = full_w // 6, full_h // 3

        # 截圖 (BGR)
        img_np = self._capture((full_x, full_y, roi_w, roi_h))

        # 2. 設定目標顏色
        lower_bound = self.mini_map_rectangle_color
        upper_bound = self.mini_map_rectangle_color

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
                
                # 過濾太小的雜訊
                if w < 50 or h < 50:
                    continue
                
                area = w * h
                if area > max_area:
                    max_area = area
                    best_rect = (x, y, w, h)

            # 回傳絕對座標
            if best_rect:
                rect_x, rect_y, rect_w, rect_h = best_rect
                self.mini_map_area = rect_x, rect_y, rect_w, rect_h
                return self.mini_map_area
        
        return 0, 0, 0, 0

    def get_character_position(self, color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。
        :param color_tolerance: int, 顏色容忍度
        :return: "left", "right", or "not_found"
        """
        # 1. 擷取小地圖畫面
        img_np = self.get_mini_map_area_screenshot()
        
        # 2. 計算整張圖每個像素與目標顏色的差異
        diff_matrix = np.sum(np.abs(img_np - self.my_character_color), axis=2)
        
        # 3. 篩選符合容忍度的像素 (Boolean Mask)
        mask = diff_matrix < (color_tolerance * 3)
        
        # 4. 找出所有符合條件的座標 (y, x)
        _, x_coords = np.where(mask)

        if x_coords.size == 0:
            return "not_found"

        # 5. 計算平均 X 座標並判斷位置
        avg_x = np.mean(x_coords)
        width = img_np.shape[1]
        
        if avg_x < width / 2:
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
        img_np = self.get_mini_map_area_screenshot()
        
        # 2. 計算色差並建立遮罩
        diff_matrix = np.sum(np.abs(img_np - self.other_player_color), axis=2)
        mask = (diff_matrix < (color_tolerance * 3)).astype(np.uint8) * 255

        # 3. 使用 3x3 Kernel 進行腐蝕 (Erosion)
        kernel = np.ones((3, 3), np.uint8)
        eroded_mask = cv2.erode(mask, kernel, iterations=1)

        # 4. 如果腐蝕後還有殘留像素，代表地圖上有符合大小的紅點
        return cv2.countNonZero(eroded_mask) > 0

    def has_rune(self, color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有輪（符文）。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :return: bool
        """
        # 1. 擷取小地圖畫面
        img_np = self.get_mini_map_area_screenshot()
        
        # 2. 計算色差並建立遮罩
        diff_matrix = np.sum(np.abs(img_np - self.rune_color), axis=2)
        mask = (diff_matrix < (color_tolerance * 3)).astype(np.uint8) * 255

        # 3. 使用 3x3 Kernel 進行腐蝕 (Erosion)
        kernel = np.ones((3, 3), np.uint8)
        eroded_mask = cv2.erode(mask, kernel, iterations=1)

        # 4. 如果腐蝕後還有殘留像素，代表地圖上有符合大小的輪的色塊
        return cv2.countNonZero(eroded_mask) > 0

    def get_player_pos(self) -> tuple[int, int] | None:
        """
        獲取玩家在小地圖上的座標 (x, y)
        """
        img_np = self.get_mini_map_area_screenshot()
        
        diff_matrix = np.sum(np.abs(img_np - self.my_character_color), axis=2)
        mask = (diff_matrix < 30).astype(np.uint8) * 255
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                return cX, cY
        return None

    def get_rune_pos(self) -> tuple[int, int] | None:
        """
        獲取符文在小地圖上的座標 (x, y)
        """
        img_np = self.get_mini_map_area_screenshot()
        
        diff_matrix = np.sum(np.abs(img_np - self.rune_color), axis=2)
        mask = (diff_matrix < 30).astype(np.uint8) * 255
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                return cX, cY
        return None

    def _match_template(self, scene_img, template, threshold=0.9):
        """
        OpenCV 模板匹配助手
        :param scene_img: 被搜尋的圖片 (BGR NumPy Array)
        :param template: 模板圖片 (Path, PIL Image, or NumPy Array)
        :param threshold: 信心門檻值
        :return: (found: bool, rect: tuple(x, y, w, h) or None)
        """
        if scene_img is None:
            return False, None

        # 準備模板圖片
        if isinstance(template, (str, Path)):
            template_img = cv2.imread(str(template))
        elif isinstance(template, PIL.Image.Image):
            template_img = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
        elif isinstance(template, np.ndarray):
            template_img = template
        else:
            return False, None

        if template_img is None:
            return False, None

        # 執行匹配
        try:
            res = cv2.matchTemplate(scene_img, template_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val >= threshold:
                h, w = template_img.shape[:2]
                # max_loc 是左上角座標 (x, y)
                return True, (max_loc[0], max_loc[1], w, h)
            else:
                return False, None
        except Exception as e:
            print(f"Error in match_template: {e}")
            return False, None

    def is_on_screen(self, pic: PIL.Image.Image | str | Path, img=None) -> bool:
        """
        辨識想要找的東西在不在畫面上
        :param pic: 想要辨識的圖片
        :param img: 一張截圖，沒有傳入就會自動擷取一張
        :return: bool
        """
        if img is None:
            img = self.get_full_screen_screenshot()

        found, _ = self._match_template(img, pic, threshold=0.99)
        return found

    def find_image_location(self, pic_for_search: str | PIL.Image.Image | Path) -> tuple[int, int] | None:
        """
        用於辨識按鈕之後移動
        :param pic_for_search: 要辨識的圖片
        :return: tuple (dx, dy)
        """
        try:
            # 使用 win32api 獲取滑鼠位置
            current_mouse_x, current_mouse_y = win32api.GetCursorPos()

            screenshot = self.get_full_screen_screenshot()
            found, rect = self._match_template(screenshot, pic_for_search, threshold=0.99)

            if found and rect:
                box_left, box_top, box_width, box_height = rect

                win_x, win_y, _, _ = self.maple_full_screen_area
                
                # 計算目標中心點
                target_x = win_x + box_left + box_width / 2
                target_y = win_y + box_top + box_height / 2

                dx = int(target_x - current_mouse_x)
                dy = int(target_y - current_mouse_y)

                return dx, dy
            else:
                print(f'畫面中找不到{pic_for_search}')
                return None

        except Exception as e:
            print(f"Error in find_image_location: {e}")
            return None