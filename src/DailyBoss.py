import time
import PIL.Image
from src.MapleScript import MapleScript
from src.XiaoController import XiaoController
from src.DailyPrepare import DailyPrepare


class DailyBoss(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__daily_helper = DailyPrepare(controller=controller)
        self.__boss_dict = self.yaml_loader.boss_dict
        self.__move_to_boss_map_button = PIL.Image.open(self.get_photo_path("boss_ui_move_to_boss_map_button.png"))

    def check_daily_boss_progress(self):
        """
        檢查每日Boss的進度
        :return: 一個包含所有沒打過得Boss的list
        """
        # 先打開到行事曆的界面
        self.__daily_helper.invoke_menu()
        self.find_and_click_image(self.get_photo_path("daily_schedule.png"))

        # 滑鼠移動到每週Boss的Tab並且往下滑
        self.find_and_click_image(self.get_photo_path("schedule_weekly_tab.png"))
        self.scroll_down()
        self.find_and_click_image(self.get_photo_path("schedule_boss_tab.png"))

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
        # 打開Boss界面，然後切到炎魔那頁之後過去
        self.press_and_wait("t", 0.7)
        self.find_and_click_image(self.get_photo_path("boss_ui_zakum.png"))
        self.find_and_click_image(self.__move_to_boss_map_button)

        # 移動到炎魔入口，確保我們選到的是普通的炎魔難度，然後選完接收炎魔碎片之後入場
        self.replay_script([('press', 'right', 1.82), ('release', 'right', 11.17), ('press', 'up', 11.79), ('release', 'up', 11.88)])
        for _ in range(2):
            self.press_and_wait("up")
        self.press_and_wait(["down", "enter", "right", "enter"])
        while not self.is_on_screen(self.get_photo_path("zakum_map.png")):
            time.sleep(1)

        # 移動到祭壇那邊，然後把火焰之眼丟出去
        self.press_and_wait("space")
        self.press_and_wait("i", 0.5)
        self.find_and_click_image(self.get_photo_path("item_others_tab.png"))
        self.find_and_click_image(self.get_photo_path("eye_of_fire.png"))
        self.move((-600, 0))
        self.click()
        self.press_and_wait("esc")

        # 等待炎魔生成
        time.sleep(3.5)

        # 開打，接著調整人物讓寵物撿東西
        self.press_and_wait("end", 1)
        self.press_and_wait(["left", "space", "space", "right", "space", "space", "space"], 0.7)

        # 離開地圖
        self.press_and_wait(["y", "right", "enter"])
        time.sleep(1)

        # 回到村莊
        self.replay_script([('press', 'left', 1.92), ('release', 'left', 2.37), ('press', 'up', 2.81), ('release', 'up', 2.91)])

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
            'magnus': self.mock_boss_work,
            'hilla': self.mock_boss_work,
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
