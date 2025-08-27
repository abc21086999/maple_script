from MapleScript import MapleScript
from XiaoController import XiaoController
import time


class DailyBoss(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller)
        self.move_to_boss_map_button = self.get_photo_path("move_to_boss_button.png")


    def von_leon(self):
        """
        打凡雷恩
        :return: None
        """
        self.press_and_wait("t", 0.5)  # 打開Boss界面
        self.find_and_click_image(self.get_photo_path("von_leon_tab.png"))  # 點下凡雷恩的選項
        if self.is_on_screen(self.get_photo_path("von_leon_completed.png")):  # 如果打過了就跳過
            self.press_and_wait("esc")
            return None
        self.find_and_click_image(self.move_to_boss_map_button)  # 點下移動到Boss地圖的按鈕
        time.sleep(2)  # 等待地圖轉換
        for i in range(4):
            self.press("right")  # 向右邊移動一點
        time.sleep(1)  # 緩衝
        for i in range(3):
            self.press_and_wait("space", 1) # 向右邊滑動
        self.press_and_wait("up")  # 在傳點按上
        self.press_and_wait("enter")  # 過傳點
        time.sleep(1.5)  # 等待地圖轉換
        for i in range(6):
            self.press_and_wait("space", 0.8)  # 移動到凡雷恩旁邊
        self.press_and_wait("y")  # 按下對話鍵
        self.press_and_wait("right")  # 選擇接受
        self.press_and_wait("enter", 6)  # 按Enter召喚Boss
        self.press_and_wait("end", 1.5)  # 打掉之後等待寵物撿東西
        self.press_and_wait("left")  # 角色向左
        for i in range(7):
            self.press_and_wait("space", 0.8)  # 移動到傳點旁邊
        for i in range(4):
            self.press("right")  # 移動到傳點然後過傳點
        self.press_and_wait("up")
        self.press_and_wait("right")
        self.press("enter")
        return None


    def horntail(self):
        """
        打闇黑龍王
        :return: None

         """
        self.press_and_wait("t", 0.5)  # 打開Boss界面
        self.find_and_click_image(self.get_photo_path("horntail_tab.png"))  # 點下闇黑龍王的選項
        self.find_and_click_image(self.move_to_boss_map_button)  # 點下移動到Boss地圖的按鈕
        time.sleep(2)  # 等待地圖轉換
        self.find_and_click_image(self.get_photo_path("horntail_enrty.png"))  # 點下遠征隊標誌
        self.press_and_wait("enter", 6)
        self.press_and_wait("end")
        time.sleep(2)
        for i in range(2):
            self.press_and_wait("space", 1)
        for i in range(2):
            self.press_and_wait("alt", 0.2)
        time.sleep(0.5)
        self.press_and_wait("left")
        self.press_and_wait("up")



if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = DailyBoss(Xiao)
        # Maple.von_leon()
        Maple.horntail()