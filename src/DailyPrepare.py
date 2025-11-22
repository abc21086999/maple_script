import time
from src.XiaoController import XiaoController
from src.MapleScript import MapleScript


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__images = self.yaml_loader.daily_prepare_images

    def switch_to_grinding_set(self):
        """
        切換到練功用的角色設定
        :return: None
        """
        imgs = self.__images['settings']

        while not self.is_maple_focus():
            time.sleep(0.1)
        if self.is_maple_focus():
            # 打開角色套組設定的界面
            self.press("f11")
            time.sleep(0.3)

            # 移動過去練功的圖案，並且點下去
            self.find_and_click_image(imgs['daily_set'])

            # 移動過去套用按鈕，並且點下去
            self.find_and_click_image(imgs['daily_apply'])

            # 如果有東西不一樣（出現確認按鈕）需要切換，再按下Enter
            if self.is_on_screen(imgs['confirm_popup']):
                self.press_and_wait("enter")

            # 最後不管怎麼樣，都要用Esc將界面關閉
            self.press_and_wait("esc")

            # 檢查開關技能有沒有開啟
            if not (self.is_on_screen(imgs['buff_storm']) or
                    self.is_on_screen(imgs['buff_trifling']) or
                    self.is_on_screen(imgs['buff_guided_arrow'])):
                self.press_and_wait("=", 1)


    def collect_union_coin(self):
        """
        蒐集戰地聯盟的硬幣
        :return: None
        """
        imgs = self.__images['union']

        if self.is_maple_focus():
            # 打開戰地聯盟的界面
            self.press_and_wait("f10")
            while not self.is_on_screen(imgs['get_coin']):
                time.sleep(0.1)

            # 按下拿硬幣的按鈕，接著按Enter關掉確認畫面
            self.find_and_click_image(imgs['get_coin'])
            self.press_and_wait("enter")

            # 切換到神器頁面
            self.find_and_click_image(imgs['artifact_tab'])
            while not self.is_on_screen(imgs['extend_button']):
                time.sleep(0.1)

            # 點擊延長按鈕
            self.find_and_click_image(imgs['extend_button'])
            if self.is_on_screen(imgs['extend_error']):
                self.press_and_wait("enter")
            else:
                self.find_and_click_image(imgs['extend_confirm'])


            # 最後按Esc離開
            self.press_and_wait("esc")


    def start_daily_or_weekly_mission(self):
        """
        開始或結束每日或是每週任務
        :return: None
        """
        imgs = self.__images['mission']

        if self.is_maple_focus():
            # 打開每日任務的界面
            self.invoke_menu()
            self.find_and_click_image(imgs['daily_schedule'])

            # 如果有開始任務的按鈕，那就按下去
            if self.is_on_screen(imgs['daily_start']):
                self.find_and_click_image(imgs['daily_start'])

            # 如果有已經可以完成的任務，那就完成
            if self.is_on_screen(imgs['daily_complete']):
                self.find_and_click_image(imgs['daily_complete'])
                self.find_and_click_image(imgs['panel_confirm'])

                # 有額外的活動獎勵
                if self.is_on_screen(imgs['daily_bonus']):
                    self.find_and_click_image(imgs['daily_bonus'])

            # 開始每週任務
            if self.is_on_screen(imgs['weekly_start']):
                # 點下開始每週任務的按鈕
                self.find_and_click_image(imgs['weekly_start'])

                # 選擇『是』
                self.press_and_wait("right")

                for i in range(2):
                    self.press_and_wait("enter")

            # 如果有可以完成的每週任務，那就完成它
            if self.is_on_screen(imgs['weekly_complete']):
                self.find_and_click_image(imgs['weekly_complete'])

                # 選擇『是』
                self.press_and_wait("right")

                for i in range(2):
                    self.press_and_wait("enter")

            # 不管怎麼樣最後要把界面關閉
            self.press("esc")


    def dismantle_armours(self):
        """
        分解裝備
        :return: None
        """
        imgs = self.__images['dismantle']

        if self.is_maple_focus():
            # 點下快速移動的界面
            self.find_and_click_image(imgs['fast_travel'])

            # 點下技術村的圖案
            self.find_and_click_image(imgs['village_icon'])

            # 點下『是』，去到技術村
            self.press_and_wait("right")
            self.press_and_wait("enter")

            # 移動中
            while not self.is_on_screen(imgs['village_map_check']):
                time.sleep(0.5)

            # 打開裝備欄
            self.press_and_wait("i")
            while not self.is_on_screen(imgs['panel_button']):
                time.sleep(0.1)

            # 點下分解裝備的按鈕
            self.find_and_click_image(imgs['panel_button'])

            # 點下把裝備放上分解面板的按鈕
            self.find_and_click_image(imgs['put_armor'])

            # 在點了之後如果沒有裝備被放上面板，那就離開，反之就進行分解
            while not self.is_on_screen(imgs['empty_table']):
                # 滑鼠移動到地圖icon以減少干擾
                self.find_and_click_image(imgs['village_map_check'])

                # 點下分解按鈕
                self.find_and_click_image(imgs['disassemble_button'])

                # 確定分解並等待
                self.press_and_wait("enter")
                while not self.is_on_screen(imgs['complete_popup']):
                    time.sleep(0.1)

                # 確認分解完成的訊息
                self.press_and_wait("enter")

                # 再點一次將裝備放上的按鈕
                self.find_and_click_image(imgs['put_armor'])

            # 最後都沒有裝備要分解了，按兩下Esc以關閉分解界面和裝備界面
            print("裝備分解完成")
            for i in range(2):
                self.press_and_wait("esc", 0.1)

            # 按下上來離開技術村
            self.press_and_wait("up", 1.5)


    def receive_hd_gift(self):
        """
        領取HD禮物
        :return: None
        """
        imgs = self.__images['hd']

        if self.is_maple_focus():
            # 打開總攬菜單
            self.invoke_menu()

            # 點下HD按鈕，然後移動滑鼠避免干擾
            self.find_and_click_image(imgs['icon'])
            self.find_and_click_image(imgs['safe_spot_click'])

            # 如果這個月都已經領完了，那就離開
            if self.is_on_screen(imgs['all_received']):
                for i in range(2):
                    self.press("esc")

            # 如果有HD可以領，就點下領取獎勵的按鈕
            elif self.is_on_screen(imgs['receive_button']):
                self.find_and_click_image(imgs['receive_button'])

                # 如果有可以領取的禮物（考量到禮拜天可以領兩次所以就用while）
                while self.is_on_screen(imgs['has_gift']):
                    self.find_and_click_image(imgs['take_coin'])

                    # 關閉領完之後的確認頁面
                    self.press_and_wait("esc")

                    # 再按一次
                    self.find_and_click_image(imgs['receive_button'])

                # 最後把HD界面關閉
                for i in range(2):
                    self.press("esc")

            # 不然就直接離開HD界面
            else:
                self.press("esc")
            time.sleep(0.5)


    def receive_milestones(self):
        """
        領取里程
        :return: None
        """
        imgs = self.__images['milestone']

        if self.is_maple_focus():
            # 打開總攬菜單
            self.invoke_menu()

            # 點下里程的圖案
            self.find_and_click_image(imgs['icon'])

            # 如果有里程可以領
            if self.is_on_screen(imgs['has_collectable']):
                # 按下『領取里程』
                self.find_and_click_image(imgs['confirm'])

            # 不然就將里程視窗關閉
            elif self.is_on_screen(imgs['no_milestone']):
                self.press_and_wait("esc")

    def collect_market(self):
        """
        處理拍賣
        :return: None
        """
        imgs = self.__images['market']

        if self.is_maple_focus():
            # 打開總攬菜單
            self.invoke_menu()

            # 按下拍賣 (注意：這邊使用 common 的圖示)
            self.find_and_click_image(self.__images['common']['menu_market_icon'])

            # 等待進入拍賣
            while not self.is_on_screen(imgs['title']):
                time.sleep(0.5)

            # 切換到完成的那個Tab
            self.find_and_click_image(imgs['collectable_tab'])

            # 如果有要重新上架的商品
            if self.is_on_screen(imgs['restock_all']):
                # 重新上架
                self.find_and_click_image(imgs['restock_all'])
                self.press_and_wait("enter")
                # 處理重新上架遇到位子不夠或是需要等待的狀況
                while not self.is_on_screen(imgs['restock_finish']):

                    # 如果遇到上架的時候沒位子了，那麼先把有賣掉的回收楓幣
                    if self.is_on_screen(imgs['no_vacancy']):
                        while self.is_on_screen(imgs['collect_money']):
                            self.find_and_click_image(imgs['collect_money'])
                            self.press_and_wait("enter")
                    else:
                        time.sleep(1)
                # 重新上架完按個Esc把訊息關掉
                self.press_and_wait("esc")

            self.find_and_click_image(imgs['title'])

            # 如果沒有需要重新上架，只有需要回收楓幣的
            if self.is_on_screen(imgs['all_collectable']):
                # 那就回收楓幣，回收完按個Esc把訊息關掉
                self.find_and_click_image(imgs['all_collectable'])
                self.press_and_wait("enter", 0.5)
                while not self.is_on_screen(imgs['all_collected']):
                    time.sleep(1)
                self.press_and_wait("esc")

            # 離開拍賣
            self.find_and_click_image(imgs['leave'])


    def complete_master_and_apprentice(self):
        """
        完成師徒系統
        :return: None
        """
        imgs = self.__images['master_apprentice']

        if self.is_maple_focus():
            # 打開總攬菜單，然後按下師徒
            self.invoke_menu()
            self.find_and_click_image(imgs['button'])

            # 等待界面打開
            while not self.is_on_screen(imgs['title']):
                time.sleep(0.1)

            # 當界面上還有完成出現的時候，就一個一個按下去
            while self.is_on_screen(imgs['complete_button']):
                self.find_and_click_image(imgs['complete_button'])
                self.press_and_wait("enter")

            # 最後按下Esc來離開師徒界面
            time.sleep(0.3)
            self.press_and_wait("esc")


    def handle_housing(self):
        """
        處理小屋每日對話
        :return: None
        """
        imgs = self.__images['housing']

        # 打開總攬界面
        self.invoke_menu()

        # 切換到我的小屋的選項
        self.press_and_wait("tab")
        for i in range(3):
            self.press_and_wait("right")
        self.press_and_wait("up")

        # 然後按下Enter
        for i in range(2):
            self.press_and_wait("enter", 0.7)

        # 等待到達小屋
        while not self.is_on_screen(imgs['house_map_check']):
            time.sleep(0.5)

        # 向前移動兩次
        for i in range(2):
            self.press_and_wait("space", 0.7)

        # 跟管家對話
        self.press_and_wait("y")

        # 如果有可以對話（這段還有改善空間但是先這樣寫ㄅ）
        if self.is_on_screen(imgs['talk_caretaker']):
            for i in range(6):
                self.press_and_wait("y")

        # 如果有多按導致跳出對話視窗就關掉
        while self.is_on_screen(imgs['stop_conversation']):
            time.sleep(0.3)
            self.press_and_wait("esc")

        # 打開總攬界面離開小屋
        self.invoke_menu()

        # 切換到我的小屋的選項然後離開
        self.press_and_wait("tab")
        for i in range(3):
            self.press_and_wait("right")
        self.press_and_wait(["up", "enter", "down", "enter"])

    def start(self):
        """
        執行所有的每日行程
        """
        self.switch_to_grinding_set()
        self.collect_union_coin()
        self.start_daily_or_weekly_mission()
        self.dismantle_armours()
        self.receive_hd_gift()
        self.receive_milestones()
        self.collect_market()
        self.complete_master_and_apprentice()
        self.handle_housing()


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
        Maple.handle_housing()