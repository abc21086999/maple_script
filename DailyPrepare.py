import time
from XiaoController import XiaoController
from MapleScript import MapleScript
import PIL.Image


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def switch_to_grinding_set(self):
        """
        切換到練功用的角色設定
        :return: None
        """
        # 打開角色套組設定的界面
        self.press("f11")
        time.sleep(0.3)

        # 移動過去練功的圖案，並且點下去
        self.find_and_click_image(self.get_photo_path("daily_set.png"))
        time.sleep(0.3)

        # 移動過去套用按鈕，並且點下去
        self.find_and_click_image(self.get_photo_path("daily_apply.png"))
        time.sleep(0.3)

        # 如果有東西不一樣（出現確認按鈕）需要切換，再按下Enter
        if self.is_on_screen(self.get_photo_path("confirm_daily_pop_up.png")):
            self.press("enter")
        time.sleep(0.3)

        # 最後不管怎麼樣，都要用Esc將界面關閉
        self.press("esc")

    def collect_union_coin(self):
        """
        蒐集戰地聯盟的硬幣
        :return: None
        """
        # 打開戰地聯盟的界面
        self.press("f10")
        time.sleep(1)

        # 按下拿硬幣的按鈕，接著用Enter關掉確認界面
        self.find_and_click_image(self.get_photo_path("get_coin.png"))
        time.sleep(0.5)
        self.press("enter")
        self.press("esc")
        time.sleep(0.3)

    def start_daily_or_weekly_mission(self):
        """
        開始或結束每日或是每週任務
        :return: None
        """
        # 打開每日任務的界面
        self.find_and_click_image(self.get_photo_path("daily_schedule.png"))
        time.sleep(0.3)

        # 如果有開始任務的按鈕，那就按下去
        daily_start_button = PIL.Image.open(self.get_photo_path("schedule_daily_all_start.png"))
        if self.is_on_screen(daily_start_button):
            self.find_and_click_image(daily_start_button)
            time.sleep(0.3)

        # 如果有已經可以完成的任務，那就完成
        daily_finish_button = PIL.Image.open(self.get_photo_path("schedule_daily_all_complete.png"))
        if self.is_on_screen(daily_finish_button):
            self.find_and_click_image(daily_finish_button)
            time.sleep(0.3)
            self.find_and_click_image(self.get_photo_path("schedule_panel_confirm.png"))
            time.sleep(0.3)

        # 開始每週任務
        weekly_mission_start_button = PIL.Image.open(self.get_photo_path("weekly_mission_start_button.png"))
        if self.is_on_screen(weekly_mission_start_button):
            # 點下開始每週任務的按鈕
            self.find_and_click_image(weekly_mission_start_button)
            time.sleep(0.3)

            # 選擇『是』
            self.press("right")
            time.sleep(0.3)

            for i in range(2):
                self.press("enter")
                time.sleep(0.3)

        # 如果有可以完成的每週任務，那就完成它
        complete_weekly_mission = PIL.Image.open(self.get_photo_path("complete_weekly_mission_button.png"))
        if self.is_on_screen(complete_weekly_mission):
            self.find_and_click_image(complete_weekly_mission)
            time.sleep(0.3)

            # 選擇『是』
            self.press("right")
            time.sleep(0.3)

            for i in range(2):
                self.press("enter")
                time.sleep(0.3)

        # 不管怎麼樣最後要把界面關閉
        self.press("esc")

    def dismantle_armours(self):
        # 點下快速移動的界面
        self.find_and_click_image(self.get_photo_path("fast_travel.png"))
        time.sleep(0.3)

        # 點下技術村的圖案
        self.find_and_click_image(self.get_photo_path("village.png"))
        time.sleep(0.3)

        # 點下『是』，去到技術村
        self.press("right")
        time.sleep(0.3)

        # 移動中
        self.press("enter")
        time.sleep(1.5)

        # 打開裝備欄
        self.press("i")
        time.sleep(0.8)

        # 點下分解裝備的按鈕
        self.find_and_click_image(self.get_photo_path("disassemble_panel.png"))
        time.sleep(0.3)

        # 點下把裝備放上分解面板的按鈕
        self.find_and_click_image(self.get_photo_path("put_all_armor_on_table.png"))
        time.sleep(0.3)

        # 在點了之後如果沒有裝備被放上面板，那就離開，反之就進行分解
        while not self.is_on_screen(self.get_photo_path("empty_disassembly_table.png")):
            # 滑鼠移動到面板header以減少干擾
            self.find_and_click_image(self.get_photo_path("disassembly_table_header.png"))
            time.sleep(0.3)

            # 點下分解按鈕
            self.find_and_click_image(self.get_photo_path("disassemble.png"))
            time.sleep(0.3)

            # 確定分解並等待
            self.press("enter")
            time.sleep(4)

            # 確認分解完成的訊息
            self.press("enter")
            time.sleep(0.3)

            # 再點一次將裝備放上的按鈕
            self.find_and_click_image(self.get_photo_path("put_all_armor_on_table.png"))
            time.sleep(0.3)

        # 最後都沒有裝備要分解了，按兩下Esc以關閉分解界面和裝備界面
        print("裝備分解完成")
        for i in range(2):
            self.press("esc")
            time.sleep(0.1)

        # 按下上來離開技術村
        self.press("up")

    def receive_hd_gift(self):
        # TODO: 打開HD -> 如果有禮物可以領，那就領（還要記得依據什麼禮物要領什麼不要這樣來決定） -> 如果沒有就關掉
        """
        領取HD禮物
        :return: None
        """
        pass

    def receive_milestones(self):
        # TODO: 點開里程的圖案 -> 選第二個選項 -> 如果有要領的里程就點下去 ->再去處理里程已經領完的狀況
        """
        領取里程
        :return: None
        """
        pass


if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = DailyPrepare(controller)
        Maple.switch_to_grinding_set()
        Maple.collect_union_coin()
        Maple.start_daily_or_weekly_mission()
        Maple.dismantle_armours()
