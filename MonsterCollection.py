import time
from XiaoController import XiaoController
from MapleScript import MapleScript


class MonsterCollection(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def collect_monster_collection(self):
        # 打開怪物蒐藏界面
        self.press("f10")
        time.sleep(0.5)

        # 按下探險的那個Tab
        self.find_and_click_image(self.get_photo_path("adventure_tab.png"))
        time.sleep(0.3)

        # 一直截圖進行辨識，如果畫面上還有還沒領取的怪物蒐藏
        while self.is_on_screen(self.get_photo_path("receive_monster_collection_reward.png"), self.get_full_screen_screenshot()):
            # 按下領取按鈕
            self.find_and_click_image(self.get_photo_path("receive_monster_collection_reward.png"))
            time.sleep(0.2)

            # 按下Enter關閉
            self.press("enter")
            time.sleep(0.2)

            # 滑鼠回到Tab避免干擾辨識
            self.find_and_click_image(self.get_photo_path("adventure_tab.png"))
            time.sleep(0.2)

        # 最後用Esc將怪物蒐藏界面關閉
        self.press("esc")


if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = MonsterCollection(controller)
        Maple.collect_monster_collection()
