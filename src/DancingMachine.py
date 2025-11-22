import time
from src.MapleScript import MapleScript
from src.XiaoController import XiaoController
from random import uniform


class Dancing(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__direction_dict, self.__ui_dict = self.yaml_loader.dancing_config
        self.__ans_list = list()


    def start(self):
        while True:
            # 先擷取一張截圖
            sc = self.get_full_screen_screenshot()

            # 如果截圖有最後停止的UI，那就結束
            if self.is_on_screen(pic=self.__ui_dict.get("ending_npc"), img=sc):
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


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Dancing(Xiao)
        Maple.start()