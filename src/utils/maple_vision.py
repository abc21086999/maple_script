import numpy as np
import cv2
import pyautogui


class MapleVision:

    def __init__(self):
        self.mini_map_area = None
        self.other_player_color = [253, 45, 118]
        self.my_character_color = [239, 240, 12]
        self.mini_map_rectangle_color = [228, 228, 228]

    def get_mini_map_area(self, maple_x, maple_y, maple_w, maple_h):
        """
        計算小地圖在楓之谷視窗的相對位置
        :return: 小地圖在楓之谷視窗的相對位置
        """
        if self.mini_map_area is not None:
            return self.mini_map_area

        # 1. 鎖定搜尋範圍：只看視窗左上角 1/4 區域，提升效能
        full_x, full_y, full_w, full_h = maple_x, maple_y, maple_w, maple_h
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

    def get_character_position(self, maple_mini_map_area: tuple[int, int, int, int], color_tolerance=30):
        """
        分析小地圖，回傳角色位置在左邊或右邊。 (NumPy 優化版)
        :param color_tolerance: int, 顏色容忍度
        :param maple_mini_map_area, 小地圖區域
        :return: "left", "right", or "not_found"
        """
        # 1. 擷取小地圖畫面 (傳回的是 PIL Image, RGB 模式)
        minimap_img = pyautogui.screenshot(region=maple_mini_map_area, allScreens=True)

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

    def has_other_players(self, maple_mini_map_area: tuple[int, int, int, int], color_tolerance=10) -> bool:
        """
        偵測小地圖上有沒有其他玩家（紅點）。
        使用 3x3 區域檢測 (Erosion) 以過濾單個像素的雜訊。
        :param color_tolerance: int, 顏色容忍度
        :param maple_mini_map_area, 小地圖區域
        :return: bool
        """
        # 1. 擷取小地圖畫面
        minimap_img = pyautogui.screenshot(region=maple_mini_map_area, allScreens=True)
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