import time
from XiaoController import XiaoController
from MapleScript import MapleScript


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def invoke_menu(self) -> None:
        # 確保人在地圖裡面（快速旅行按鈕有出現）
        while not self.is_on_screen(self.get_photo_path("fast_travel.png")):
            time.sleep(0.3)
        # 按下漢堡選單
        self.find_and_click_image(self.get_photo_path("hamburger_menu.png"))
        # 確保有打開
        while not self.is_on_screen(self.get_photo_path("market.png")):
            time.sleep(0.3)
            self.find_and_click_image(self.get_photo_path("hamburger_menu.png"))
        return None

    def switch_to_grinding_set(self):
        """
        切換到練功用的角色設定
        :return: None
        """
        while self.is_maple_focus():
            # 打開角色套組設定的界面
            self.press("f11")
            time.sleep(0.3)

            # 移動過去練功的圖案，並且點下去
            self.find_and_click_image(self.get_photo_path("daily_set.png"))

            # 移動過去套用按鈕，並且點下去
            self.find_and_click_image(self.get_photo_path("daily_apply.png"))

            # 如果有東西不一樣（出現確認按鈕）需要切換，再按下Enter
            if self.is_on_screen(self.get_photo_path("confirm_daily_pop_up.png")):
                self.press_and_wait("enter")

            # 最後不管怎麼樣，都要用Esc將界面關閉
            self.press_and_wait("esc")

            # 檢查開關技能有沒有開啟
            if not (self.is_on_screen(self.get_photo_path("storm_elemental.png")) or
                    self.is_on_screen(self.get_photo_path("trifling_wind.png")) or
                    self.is_on_screen(self.get_photo_path("guided_arrow.png"))):
                self.press_and_wait("=", 1)
            break

    def collect_union_coin(self):
        """
        蒐集戰地聯盟的硬幣
        :return: None
        """
        while self.is_maple_focus():
            # 打開戰地聯盟的界面
            self.press_and_wait("f10")
            while not self.is_on_screen(self.get_photo_path("get_coin.png")):
                time.sleep(0.1)

            # 按下拿硬幣的按鈕，接著按Enter關掉確認畫面
            self.find_and_click_image(self.get_photo_path("get_coin.png"))
            self.press_and_wait("enter")

            # 切換到神器頁面
            self.find_and_click_image(self.get_photo_path("union_artifact_tab.png"))
            while not self.is_on_screen(self.get_photo_path("extend_union_artifact_button.png")):
                time.sleep(0.1)

            # 點擊延長按鈕
            self.find_and_click_image(self.get_photo_path("extend_union_artifact_button.png"))
            if self.is_on_screen(self.get_photo_path("extend_union_artifact_error_message.png")):
                self.press_and_wait("enter")
            else:
                self.find_and_click_image(self.get_photo_path("extend_union_artifact_confirm_button.png"))


            # 最後按Esc離開
            self.press_and_wait("esc")
            break

    def start_daily_or_weekly_mission(self):
        """
        開始或結束每日或是每週任務
        :return: None
        """
        while self.is_maple_focus():
            # 打開每日任務的界面
            self.invoke_menu()
            self.find_and_click_image(self.get_photo_path("daily_schedule.png"))

            # 如果有開始任務的按鈕，那就按下去
            daily_start_button = self.get_photo_path("schedule_daily_all_start.png")
            if self.is_on_screen(daily_start_button):
                self.find_and_click_image(daily_start_button)

            # 如果有已經可以完成的任務，那就完成
            daily_finish_button = self.get_photo_path("schedule_daily_all_complete.png")
            if self.is_on_screen(daily_finish_button):
                self.find_and_click_image(daily_finish_button)
                self.find_and_click_image(self.get_photo_path("schedule_panel_confirm.png"))

                # 有額外的活動獎勵
                bonus = self.get_photo_path("daily_bonus.png")
                if self.is_on_screen(bonus):
                    self.find_and_click_image(bonus)

            # 開始每週任務
            weekly_mission_start_button = self.get_photo_path("weekly_mission_start_button.png")
            if self.is_on_screen(weekly_mission_start_button):
                # 點下開始每週任務的按鈕
                self.find_and_click_image(weekly_mission_start_button)

                # 選擇『是』
                self.press_and_wait("right")

                for i in range(2):
                    self.press_and_wait("enter")

            # 如果有可以完成的每週任務，那就完成它
            complete_weekly_mission = self.get_photo_path("complete_weekly_mission_button.png")
            if self.is_on_screen(complete_weekly_mission):
                self.find_and_click_image(complete_weekly_mission)

                # 選擇『是』
                self.press_and_wait("right")

                for i in range(2):
                    self.press_and_wait("enter")

            # 不管怎麼樣最後要把界面關閉
            self.press("esc")
            break

    def dismantle_armours(self):
        """
        分解裝備
        :return: None
        """
        while self.is_maple_focus():
            # 點下快速移動的界面
            self.find_and_click_image(self.get_photo_path("fast_travel.png"))

            # 點下技術村的圖案
            self.find_and_click_image(self.get_photo_path("ardentmill_village_icon.png"))

            # 點下『是』，去到技術村
            self.press_and_wait("right")
            self.press_and_wait("enter")

            # 移動中
            while not self.is_on_screen(self.get_photo_path("ardentmill.png")):
                time.sleep(0.5)

            # 打開裝備欄
            self.press_and_wait("i")
            disassemble_button = self.get_photo_path("disassemble_panel.png")
            while not self.is_on_screen(disassemble_button):
                time.sleep(0.1)

            # 點下分解裝備的按鈕
            self.find_and_click_image(disassemble_button)

            # 點下把裝備放上分解面板的按鈕
            self.find_and_click_image(self.get_photo_path("put_all_armor_on_table.png"))

            # 在點了之後如果沒有裝備被放上面板，那就離開，反之就進行分解
            while not self.is_on_screen(self.get_photo_path("empty_disassembly_table.png")):
                # 滑鼠移動到地圖icon以減少干擾
                self.find_and_click_image(self.get_photo_path("ardentmill.png"))

                # 點下分解按鈕
                self.find_and_click_image(self.get_photo_path("disassemble.png"))

                # 確定分解並等待
                self.press_and_wait("enter")
                while not self.is_on_screen(self.get_photo_path("dismantle_complete.png")):
                    time.sleep(0.1)

                # 確認分解完成的訊息
                self.press_and_wait("enter")

                # 再點一次將裝備放上的按鈕
                self.find_and_click_image(self.get_photo_path("put_all_armor_on_table.png"))

            # 最後都沒有裝備要分解了，按兩下Esc以關閉分解界面和裝備界面
            print("裝備分解完成")
            for i in range(2):
                self.press_and_wait("esc", 0.1)

            # 按下上來離開技術村
            self.press_and_wait("up", 1.5)
            break

    def receive_hd_gift(self):
        """
        領取HD禮物
        :return: None
        """
        while self.is_maple_focus():
            # 打開總攬菜單
            self.invoke_menu()

            # 點下HD按鈕，然後移動滑鼠避免干擾
            self.find_and_click_image(self.get_photo_path("hd.png"))
            self.find_and_click_image(self.get_photo_path("carcion.png"))

            # 如果這個月都已經領完了，那就離開
            receive_hd_gift = self.get_photo_path("receive_hd_gift.png")
            if self.is_on_screen(self.get_photo_path("all_hd_gifts_received.png")):
                for i in range(2):
                    self.press("esc")

            # 如果有HD可以領，就點下領取獎勵的按鈕
            elif self.is_on_screen(receive_hd_gift):
                self.find_and_click_image(receive_hd_gift)

                # 如果有可以領取的禮物（考量到禮拜天可以領兩次所以就用while）
                while self.is_on_screen(self.get_photo_path("hd_has_gift.png")):
                    self.find_and_click_image(self.get_photo_path("take_hd_coin.png"))

                    # 關閉領完之後的確認頁面
                    self.press_and_wait("esc")

                    # 再按一次
                    self.find_and_click_image(receive_hd_gift)

                # 最後把HD界面關閉
                for i in range(2):
                    self.press("esc")

            # 不然就直接離開HD界面
            else:
                self.press("esc")
            time.sleep(0.5)
            break


    def receive_milestones(self):
        """
        領取里程
        :return: None
        """
        while self.is_maple_focus():
            # 打開總攬菜單
            self.invoke_menu()

            # 點下里程的圖案
            self.find_and_click_image(self.get_photo_path("milestone.png"))

            # 如果有里程可以領
            if self.is_on_screen(self.get_photo_path("has_collectable_milestones.png")):
                # 按下『領取里程』
                self.find_and_click_image(self.get_photo_path("milestone_confirm_button.png"))

            # 不然就將里程視窗關閉
            elif self.is_on_screen(self.get_photo_path("no_milestone.png")):
                self.press_and_wait("esc")
            break

    def collect_market(self):
        """
        處理拍賣
        :return: None
        """
        # 打開總攬菜單
        self.invoke_menu()

        # 按下拍賣
        self.find_and_click_image(self.get_photo_path("market.png"))

        # 等待進入拍賣
        while not self.is_on_screen(self.get_photo_path("market_title.png")):
            time.sleep(0.5)

        # 切換到完成的那個Tab
        self.find_and_click_image(self.get_photo_path("market_collectable_tab.png"))

        # 如果有要重新上架的商品
        if self.is_on_screen(self.get_photo_path("re_stock_all.png")):
            # 重新上架
            self.find_and_click_image(self.get_photo_path("re_stock_all.png"))
            self.press_and_wait("enter")
            # 處理重新上架遇到位子不夠或是需要等待的狀況
            while not self.is_on_screen(self.get_photo_path("re_stock_finish.png")):

                # 如果遇到上架的時候沒位子了，那麼先把有賣掉的回收楓幣
                if self.is_on_screen(self.get_photo_path("no_vacancy_in_market.png")):
                    collect_money = self.get_photo_path("collect_money.png")
                    while self.is_on_screen(collect_money):
                        self.find_and_click_image(collect_money)
                        self.press_and_wait("enter")
                else:
                    time.sleep(1)
            # 重新上架完按個Esc把訊息關掉
            self.press_and_wait("esc")

        self.find_and_click_image(self.get_photo_path("market_title.png"))

        # 如果沒有需要重新上架，只有需要回收楓幣的
        if self.is_on_screen(self.get_photo_path("all_collectable.png")):
            # 那就回收楓幣，回收完按個Esc把訊息關掉
            self.find_and_click_image(self.get_photo_path("all_collectable.png"))
            self.press_and_wait("enter", 0.5)
            while not self.is_on_screen(self.get_photo_path("all_collected.png")):
                time.sleep(1)
            self.press_and_wait("esc")

        # 離開拍賣
        self.find_and_click_image(self.get_photo_path("leave_market.png"))


    def complete_master_and_apprentice(self):
        """
        完成師徒系統
        :return: None
        """
        # 打開總攬菜單，然後按下師徒
        self.invoke_menu()
        self.find_and_click_image(self.get_photo_path("master_and_apprentice_button.png"))

        # 等待界面打開
        while not self.is_on_screen(self.get_photo_path("master_and_apprentice_title.png")):
            time.sleep(0.1)

        # 當界面上還有完成出現的時候，就一個一個按下去
        complete_button = self.get_photo_path("master_and_apprentice_complete_button.png")
        while self.is_on_screen(complete_button):
            self.find_and_click_image(complete_button)

        # 最後按下Esc來離開師徒界面
        time.sleep(0.3)
        self.press_and_wait("esc")


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = DailyPrepare(Xiao)
        Maple.switch_to_grinding_set()
        Maple.collect_union_coin()
        Maple.start_daily_or_weekly_mission()
        Maple.dismantle_armours()
        Maple.receive_hd_gift()
        Maple.receive_milestones()
        Maple.collect_market()
        Maple.complete_master_and_apprentice()
