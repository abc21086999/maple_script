import time
from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController


class DailyBoss(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__images = self.yaml_loader.daily_boss_images
        self.__common_images = self.yaml_loader.daily_prepare_images
        self.__boss_dict = self.yaml_loader.boss_dict

    def __got_to_boss_map(self, boss: str):
        # 直接從字典中取得對應 Boss 的 Tab 圖片
        boss_tab_img = self.__images[boss]['tab_pic']
        
        # 打開Boss界面
        self.press_and_wait("t")
        # 等待
        while not self.is_on_screen(self.__images['ui']['panel']):
            time.sleep(0.3)
        # 如果不在畫面上，那就把滑鼠移動到比較下面的地方然後往下滑
        if not self.is_on_screen(boss_tab_img):
            # 使用 Von Leon 的 Tab 作為參考點 (原本邏輯)
            self.find_and_click_image(self.__images['ui']['reference_scroll'])
            time.sleep(0.3)
            self.scroll_down()
        while not self.is_on_screen(boss_tab_img):
            time.sleep(0.3)

        self.find_and_click_image(boss_tab_img)
        self.find_and_click_image(self.__images['ui']['move_button'])

    def check_daily_boss_progress(self):
        """
        檢查每日Boss的進度
        :return: 一個包含所有沒打過得Boss的list
        """
        # 先打開到行事曆的界面 (直接呼叫父類別方法)
        self.invoke_menu()
        self.find_and_click_image(self.__common_images['mission']['daily_schedule'])

        # 滑鼠移動到每週Boss的Tab並且往下滑
        self.find_and_click_image(self.__common_images['common']['schedule_weekly_tab'])
        self.scroll_down()
        self.find_and_click_image(self.__common_images['common']['schedule_boss_tab'])

        boss_condition = []

        # 先擷取一張截圖，然後辨識每個Boss打過了沒
        screenshot = self.get_full_screen_screenshot()
        for boss_name, boss_tab_img in self.__boss_dict.items():
            # 如果Boss的tab亮著那代表沒打過
            if self.is_on_screen(pic=boss_tab_img, img=screenshot):
                boss_condition.append(boss_name)

        # 把行事曆關起來
        self.press_and_wait("esc")

        # 回傳沒打過的Boss列表
        return boss_condition

    def __zakum_work(self):
        """
        打炎魔然後撿東西，最後回到村莊
        """
        imgs = self.__images['zakum']
        
        # 打開Boss界面，然後切到炎魔那頁之後過去
        self.__got_to_boss_map("zakum")

        # 移動到炎魔入口，確保我們選到的是普通的炎魔難度，然後選完接收炎魔碎片之後入場
        self.replay_script([('press', 'right', 1.82), ('release', 'right', 11.17), ('press', 'up', 11.79), ('release', 'up', 11.88)])
        for _ in range(2):
            self.press_and_wait("up")
        self.press_and_wait(["down", "enter"])

        # 處理身上有沒有火焰之眼的的狀況
        if self.is_on_screen(imgs['npc_adobis']):
            self.press_and_wait(["right", "enter"])

        # 等待地圖移動
        while not self.is_on_screen(imgs['map_check']):
            time.sleep(1)

        # 移動到祭壇那邊，然後把火焰之眼丟出去，然後把物品欄關掉
        self.press_and_wait("space")
        self.press_and_wait("i", 0.5)
        
        # 使用 common_images 裡的 item_others_tab
        self.find_and_click_image(self.__common_images['common']['item_others_tab'])
        self.find_and_click_image(imgs['item_eye'])
        self.find_and_click_image(imgs['altar'])
        self.press_and_wait("esc")

        # 等待炎魔生成
        time.sleep(3.5)

        # 開打，接著調整人物讓寵物撿東西
        self.press_and_wait("end", 1)
        self.press_and_wait(["left", "space", "space", "right", "space", "space", "space"], 0.7)

        # 離開地圖
        self.press_and_wait(["y", "right", "enter"])

    def __arkarium_work(self):
        self.__got_to_boss_map("arkarium")

    def __magnus_work(self):
        imgs = self.__images['magnus']
        self.__got_to_boss_map("magnus")
        while not self.is_on_screen(imgs['castle_map_icon']):
            time.sleep(0.5)
        self.press_and_wait(["space", "y", "up", "up", "down", "enter"], wait_time=0.5)
        while not self.is_on_screen(imgs['map_check']):
            time.sleep(0.5)
        self.key_down("a")
        time.sleep(0.5)
        self.key_down("right")
        time.sleep(10)
        self.key_up("a")
        time.sleep(0.5)
        self.key_up("right")
        time.sleep(0.5)
        self.key_down("left")
        time.sleep(10)
        self.key_up("left")

    def __hilla_work(self):
        imgs = self.__images['hilla']
        self.__got_to_boss_map("hilla")
        while not self.is_on_screen(imgs['tower_map_icon']):
            time.sleep(1)
        self.press_and_wait(["space", "space", "y", "up", "enter"], wait_time=0.7)


    def mock_boss_work(self):
        pass

    def decide_daily_boss_schedule(self):
        """
        決定這一次運行有什麼Boss需要打
        :return:
        """
        # 一個Boss名稱和對應的工作的對應表
        boss_work_mapping_dict = {
            'zakum': self.__zakum_work,
            'magnus': self.__magnus_work,
            'hilla': self.__hilla_work,
            'pierre': self.mock_boss_work,
            'von_bon': self.mock_boss_work,
            'crimson_queen': self.mock_boss_work,
            'vellum': self.mock_boss_work,
            'von_leon': self.mock_boss_work,
            'horntail': self.mock_boss_work,
            'arkarium': self.mock_boss_work,
            'pink_bean': self.mock_boss_work,
            'gollux': self.mock_boss_work,
        }
        # 拿到沒打的Boss
        boss_condition = self.check_daily_boss_progress()
        # 產生要執行的工作
        work_list = [boss_work_mapping_dict.get(i) for i in boss_condition if i in boss_work_mapping_dict]

        return work_list

    def start(self):
        """
        開始每日Boss
        """
        # 拿到所有要執行的打Boss的function
        boss_work = self.decide_daily_boss_schedule()
        # 一個一個執行
        for func in boss_work:
            func()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = DailyBoss(controller=Xiao)
        Maple.start()
