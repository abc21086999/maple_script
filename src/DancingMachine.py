import time
from src.MapleScript import MapleScript
from src.XiaoController import XiaoController


class Dancing(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.direction_dict = self.yaml_loader.dancing_dict
        self.ans_list = list()


    def start(self):
        while True:
            sc = self.get_full_screen_screenshot()
            if self.is_on_screen(pic=self.get_photo_path("") / "dancing" / "end_npc.png"):
                break
            for direction, pic in self.direction_dict.items():
                if self.is_on_screen(pic=pic, img=sc):
                    self.ans_list.append(direction)
                    print(direction)
                    time.sleep(1)
            if self.is_on_screen(pic=self.get_photo_path("") / "dancing" / "end.png", img=sc):
                print(self.ans_list)
                self.press_and_wait(self.ans_list, wait_time=0.8)
                self.ans_list.clear()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Dancing(Xiao)
        Maple.start()