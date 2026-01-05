import random
import time
from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController
from random import uniform


class Dancing(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__direction_dict, self.__ui_dict = self.yaml_loader.dancing_config
        self.__ans_list = list()

    def __start_dancing(self):
        while True:
            # 先擷取一張截圖
            sc = self.get_full_screen_screenshot()

            # 如果截圖有最後停止的UI，那就結束
            if self.is_on_screen(pic=self.__ui_dict.get("ending_npc"), img=sc):
                time.sleep(1)
                self.press_and_wait(["enter"])
                time.sleep(random.randint(10, 30))
                break

            # 否則就開始辨識如片裡面有沒有方向
            for direction, pic in self.__direction_dict.items():
                if self.is_on_screen(pic=pic, img=sc):
                    self.__ans_list.append(direction)
                    print(direction)
                    time.sleep(1)

            # 遇到開始輸入按鍵的圖示就開始輸入按鍵
            if self.is_on_screen(pic=self.__ui_dict.get("start_ui"), img=sc):
                print(self.__ans_list)
                for key in self.__ans_list:
                    self.press_and_wait(key, wait_time=uniform(0.3, 0.6))
                self.__ans_list.clear()

    def __go_to_map(self):
        self.invoke_menu()
        self.press_and_wait(["tab", "right", "right", "right", "right", "right", "enter"])
        self.find_and_click_image(self.__ui_dict.get("event_tab"))
        self.find_and_click_image(self.__ui_dict.get("participate_button"))
        self.press_and_wait(["enter", "right", "enter"])

    def start(self):
        for i in range(20):
            self.__go_to_map()
            self.__start_dancing()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Dancing(Xiao)
        Maple.start()