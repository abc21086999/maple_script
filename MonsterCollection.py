import time
from XiaoController import XiaoController
from MapleScript import MapleScript


class MonsterCollection(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def collect_and_start_monster_collection(self):
        """
        完成和重新開始怪物蒐藏
        :return: None
        """
        # 打開怪物蒐藏界面
        self.press_and_wait("f10")

        # 等待界面打開
        while not self.is_on_screen(self.get_photo_path("monster_collection_title.png")):
            time.sleep(0.5)

        # 按下探險的那個Tab
        adventure_tab = self.get_photo_path("adventure_tab.png")
        self.find_and_click_image(adventure_tab)

        # 押著Enter
        self.key_down("enter")

        # 一直截圖進行辨識，如果畫面上還有還沒領取的怪物蒐藏
        reward_button = self.get_photo_path("receive_monster_collection_reward.png")

        while self.is_on_screen(reward_button):
            # 按下領取按鈕
            self.find_and_click_image(reward_button)

            # 滑鼠回到Tab避免干擾辨識
            self.find_and_click_image(adventure_tab)

        # 一直截圖進行辨識，如果畫面上還有還沒開始的怪物蒐藏，就開始進行蒐藏
        start_button = self.get_photo_path("start_adventure.png")
        while self.is_on_screen(start_button):
            # 按下開始按鈕
            self.find_and_click_image(start_button)
            time.sleep(0.5)

        # 鬆開Enter
        self.key_up("enter")

        # 最後用Esc將怪物蒐藏界面關閉
        self.press("esc")


if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = MonsterCollection(controller)
        Maple.collect_and_start_monster_collection()
