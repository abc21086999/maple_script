import random
import time
from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController
from random import uniform


class Dancing(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__direction_dict, self.__ui_dict = self.yaml_loader.dancing_config
        self.__ans_list = list()

    def __start_dancing(self):
        while self.should_continue():
            # 先擷取一張截圖
            sc = self.get_full_screen_screenshot()

            # 如果截圖有最後停止的UI，那就結束
            if self.is_on_screen(pic=self.__ui_dict.get("ending_npc"), img=sc):
                self.sleep(1)
                self.press_and_wait(["enter"])
                # 這裡原本是 random sleep，改成可中斷的 sleep
                wait_time = random.randint(10, 30)
                self.log(f"跳舞結束，休息 {wait_time} 秒...")
                self.sleep(wait_time)
                break

            # 否則就開始辨識如片裡面有沒有方向
            for direction, pic in self.__direction_dict.items():
                if not self.should_continue(): break
                if self.is_on_screen(pic=pic, img=sc):
                    self.__ans_list.append(direction)
                    self.log(f"偵測到方向: {direction}")
                    self.sleep(1)

            # 遇到開始輸入按鍵的圖示就開始輸入按鍵
            if self.is_on_screen(pic=self.__ui_dict.get("start_ui"), img=sc):
                self.log(f"開始輸入按鍵: {self.__ans_list}")
                for key in self.__ans_list:
                    if not self.should_continue(): break
                    self.press_and_wait(key, wait_time=uniform(0.3, 0.6))
                self.__ans_list.clear()

    def __go_to_map(self):
        if not self.should_continue(): return
        self.log("正在前往跳舞地圖...")
        self.invoke_menu()
        self.press_and_wait(["tab", "right", "right", "right", "right", "right", "enter"])
        self.find_and_click_image(self.__ui_dict.get("event_tab"))
        self.find_and_click_image(self.__ui_dict.get("participate_button"))
        self.press_and_wait(["enter", "right", "enter"])

    def start(self):
        self.log("開始跳舞機腳本 (20次循環)")
        for i in range(20):
            if not self.should_continue():
                break
            self.log(f"執行第 {i+1}/20 次跳舞")
            self.__go_to_map()
            self.__start_dancing()
        self.log("跳舞機腳本結束")


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Dancing(Xiao)
        Maple.start()