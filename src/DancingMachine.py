import random
from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController


class Dancing(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__color_dict, self.__ui_dict = self.yaml_loader.dancing_config

    def __start_dancing(self):
        while self.should_continue() and self.is_maple_focus():

            # 等待開始的UI出現
            while not self.is_on_screen(self.__ui_dict["start_ui"]) and self.should_continue() and self.is_maple_focus():
                continue

            # 在結束前持續進行
            while True and self.should_continue() and self.is_maple_focus():
                sc = self.get_full_screen_screenshot()

                # 如果離開按鈕消失代表要結束了，放開按鍵並且瞪戴NPC對話框出現
                if not self.is_on_screen(pic=self.__ui_dict["leave"], img=sc):
                    self.release_all()
                    while not self.is_on_screen(pic=self.__ui_dict["ending_npc"]):
                        self.sleep(0.3)
                    # 重置一下滑鼠位置
                    self.find_and_click_image(self.__ui_dict["ending_npc"])

                    # 按下對話鍵
                    self.sleep(0.5)
                    self.press("y")
                    break

                # 如果開始UI消失那就進入Combo模式
                elif not self.is_on_screen(pic=self.__ui_dict["start_ui"], img=sc):
                    fire = ["left", "right", "space"]
                    for i in range(3):
                        random.shuffle(fire)
                        self.press_and_wait(fire, 0.05)
                        self.sleep(0.1)

                # 如果有藍色那就一直按空白
                elif self.is_on_screen(pic=self.__color_dict["blue"], img=sc):
                    for i in range(3):
                        self.press("space")
                        self.sleep(0.08)

                # 如果有粉紅色那就一直按左右鍵
                elif  self.is_on_screen(pic=self.__color_dict["pink"], img=sc):
                    for i in range(3):
                        self.press("left")
                        self.press("right")
                        self.sleep(0.08)
            break

    def __go_to_map(self):
        if not self.should_continue():
            return

        self.log("正在前往跳舞地圖...")
        self.invoke_menu()
        self.press_and_wait(["tab", "left", "left", "enter"])
        self.find_and_click_image(self.__ui_dict.get("event_tab"))
        self.sleep(0.5)
        self.press_and_wait(["enter", "right", "enter"], 0.3)

    def start(self):
        total = 5
        self.log(f"開始跳舞機腳本 ({total}次循環)")
        for i in range(total):
            if not self.should_continue() or not self.is_maple_focus():
                break
            self.log(f"執行第 {i+1}/{total} 次跳舞")
            self.__go_to_map()
            self.__start_dancing()
        self.log("跳舞機腳本結束")


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Dancing(Xiao)
        Maple.start()