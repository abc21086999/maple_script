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
        self.press_and_wait("t")
        self.find_and_click_image(self.get_photo_path("boss_ui_zakum.png"))
        self.find_and_click_image(self.__move_to_boss_map_button)

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
