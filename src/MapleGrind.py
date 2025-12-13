import PIL.Image
from src.XiaoController import XiaoController
from src.MapleScript import MapleScript
import random
import time


class MapleGrind(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__skills_list = list()
        self.__gap_time = self.yaml_loader.grind_setting
        self.__skills_dict = self.yaml_loader.skill_dict
        
        routes = self.yaml_loader.grind_routes
        self.__left_loop = routes.get('left_loop', [])
        self.__right_loop = routes.get('right_loop', [])
        
        self.__loop_map = {"left": self.__left_loop, "right": self.__right_loop, "not_found": []}

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
        # 如果list是空的，就跳過所有步驟
        if not self.__skills_list:
            return None
        # 當list有東西，而且楓之谷在前景
        while self.__skills_list and self.is_maple_focus():
            # 將按鍵一個一個按下
            key = self.__skills_list.pop()
            self.press_and_wait(key, random.uniform(*self.__gap_time))
        # 不論是list沒東西，或是楓之谷不在前景，就直接清空之後跳過
        self.__skills_list.clear()
        return None

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

    def walk_the_map(self) -> None:
        """
        根據錄製的腳本來重播操作
        """
        # 機率小於5％再來跑圖
        if random.random() < 0.05 and self.is_maple_focus():
            print("開始使用紀錄的腳本")

            recorded_events = self.__loop_map.get(self.get_character_position())
            self.replay_script(recorded_events)

    def start(self) -> None:
        try:
            while True:
                if self.is_maple_focus():
                    self.find_ready_skill()
                    self.press_ready_skills()
                    # self.move_by_pressing_up()
                    self.walk_the_map()
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
