import PIL.Image

from XiaoController import XiaoController
from MapleScript import MapleScript
import random
import time

class MapleGrind(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__position = self.get_character_position()
        self.__skills_list = list()
        self.__gap_time = self.yaml_loader.grind_setting
        self.__skills_dict = self.yaml_loader.skill_dict
        self.__left_loop = \
            [('press', 'down', 1.93), ('press', 'alt', 2.02), ('release', 'alt', 2.24), ('release', 'down', 2.29),
             ('press', 'alt', 2.95), ('release', 'alt', 3.06), ('press', 'alt', 3.14), ('release', 'alt', 3.28),
             ('press', 'alt', 3.96), ('release', 'alt', 4.07), ('press', 'alt', 4.2), ('release', 'alt', 4.34),
             ('press', 'alt', 5.16), ('release', 'alt', 5.25), ('press', 'alt', 5.37), ('release', 'alt', 5.48),
             ('press', 'alt', 6.31), ('release', 'alt', 6.39), ('press', 'alt', 6.5), ('release', 'alt', 6.63),
             ('press', 'alt', 7.61), ('release', 'alt', 7.74), ('press', 'up', 7.84), ('press', 'alt', 8.12),
             ('release', 'alt', 8.31), ('release', 'up', 8.41), ('press', 'left', 9.41), ('release', 'left', 9.47)]
        self.__right_loop = \
            [('press', 'alt', 2.07), ('release', 'alt', 2.21), ('press', 'up', 2.22), ('press', 'alt', 2.37),
             ('release', 'alt', 2.58), ('release', 'up', 2.66), ('press', 'alt', 3.48), ('release', 'alt', 3.57),
             ('press', 'alt', 3.88), ('release', 'alt', 3.99), ('press', 'alt', 4.99), ('release', 'alt', 5.11),
             ('press', 'alt', 5.27), ('release', 'alt', 5.45), ('press', 'alt', 6.22), ('release', 'alt', 6.35),
             ('press', 'alt', 6.54), ('release', 'alt', 6.7), ('press', 'alt', 7.71), ('release', 'alt', 7.82),
             ('press', 'alt', 7.96), ('release', 'alt', 8.11), ('press', 'down', 8.94), ('press', 'alt', 8.97),
             ('release', 'alt', 9.11), ('release', 'down', 9.18), ('press', 'down', 9.96), ('press', 'alt', 9.99),
             ('release', 'alt', 10.14), ('release', 'down', 10.21), ('press', 'right', 10.81),
             ('release', 'right', 10.85)]
        self.__loop_map = {"left": self.__left_loop, "right": self.__right_loop, "not_found": []}
        self.point = PIL.Image.open(self.get_photo_path("collect_point.png"))


    def find_ready_skill(self) -> None:
        """
        根據有沒有找到來決定要放哪個技能
        - 如果楓之谷不在前景，那麼就返回None
        - 如果楓之谷在前景，那麼就進行辨識
        :return: None
        """
        # 先將序列清空，避免意外
        self.__skills_list.clear()

        # 如果楓之谷不在前景，那麼就返回None
        if not self.is_maple_focus():
            return None

        # 先截一次圖，判斷各個技能準備好了沒，並根據技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個list當中
        screenshot = self.get_skill_area_screenshot()
        for skill_info in self.__skills_dict.values():
            skill_image = skill_info.get("image")
            skill_key = skill_info.get("key")
            if self.is_on_screen(skill_image, screenshot):
                self.__skills_list.append(skill_key)

        # 隨機的加入不需要圖片辨識的妖精護盾
        # for i in range(random.randint(0, 1)):
        #     self.skills_list.append("ctrl")

        # 用shuffle以增加隨機性
        random.shuffle(self.__skills_list)
        return None


    def press_ready_skills(self) -> None:
        """
        將技能一個一個按下去
        如果楓之谷不在前景，那麼就會清空
        :return:
        """
        self.get_point()
        # 如果list是空的，就跳過所有步驟
        if not self.__skills_list:
            return None
        # 當list有東西，而且楓之谷在前景
        while self.__skills_list and self.is_maple_focus():
            # 將按鍵一個一個按下
            key = self.__skills_list.pop()
            self.press_and_wait(key, random.uniform(*self.__gap_time))
            self.get_point()
        # 不論是list沒東西，或是楓之谷不在前景，就直接清空之後跳過
        self.__skills_list.clear()
        return None

    def get_point(self):
        """
        點那個蒐集點數的圖案
        :return:
        """
        if self.is_on_screen(self.point):
            self.find_and_click_image(self.point)

    def move_by_pressing_up(self) -> None:
        """
        隨機（20％的機率）按下上，來透過傳點移動
        :return: None
        """
        if self.is_maple_focus() and random.random() < 0.3:
            self.press("up")
            time.sleep(random.uniform(*self.__gap_time))

    def move_by_grappling(self) -> None:
        if (self.is_maple_focus() and
            self.is_on_screen(self.get_photo_path("grappling.png")) and
            random.random() < 0.1):
            self.press_and_wait("8", 2)
            time.sleep(random.uniform(*self.__gap_time))
            self.key_down("down")
            self.press("alt")
            self.key_up("down")

    def replay_script(self) -> None:
        """
        根據錄製的腳本來重播操作
        """
        # 機率小於5％再來跑圖
        if random.random() < 0.05 and self.is_maple_focus():
            print("開始使用紀錄的腳本")

            recorded_events = self.__loop_map.get(self.get_character_position(), [])

            start_replay_time = time.time()
            for action, key_str, event_time in recorded_events:
                if not self.is_maple_focus():
                    print("楓之谷不在前景，中止跑圖")
                    break
                target_time = start_replay_time + event_time
                sleep_duration = target_time - time.time()
                if sleep_duration > 0:
                    time.sleep(sleep_duration)

                if action == 'press':
                    self.key_down(key_str)
                elif action == 'release':
                    self.key_up(key_str)

            print("腳本重播完畢")

    def start(self) -> None:
        try:
            while True:
                if self.is_maple_focus():
                    self.find_ready_skill()
                    self.press_ready_skills()
                    self.move_by_pressing_up()
                    # self.replay_script()
                    time.sleep(1)
                else:
                    time.sleep(1)
                    continue
        except KeyboardInterrupt:
            print(f'腳本中止')


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = MapleGrind(Xiao)
        Maple.start()
