from src.utils.xiao_controller import XiaoController
from src.MapleScript import MapleScript
from functools import cached_property
from pathlib import Path
import PIL.Image
import random
import time


class MapleGrind(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__skills_list = list()
        self.__gap_time = self.yaml_loader.grind_setting
        self.__settings = self.settings.get("grind_settings")
        
        routes = self.yaml_loader.grind_routes
        self.__loop_map = {"left": routes.get('left_loop', []), "right": routes.get('right_loop', []), "not_found": []}

    @cached_property
    def user_skills(self) -> list:
        """
        從 settings.yaml 讀取使用者自定義的練功技能，並載入圖片。
        使用 cached_property 確保只載入一次。
        Returns:
            list[dict]: [{'key': 'a', 'image': PIL.Image}, ...]
        """
        # 1. 取得純資料
        raw_skills = self.settings.get('grind_skills', default=[])
        
        if not isinstance(raw_skills, list):
            return []

        loaded_skills = []
        project_root = Path(__file__).resolve().parent.parent

        for item in raw_skills:
            # 必須啟用且有圖片路徑
            if not item.get('enabled', False) or not item.get('image_path'):
                continue

            path_str = item.get('image_path')
            img_path = Path(path_str)
            
            # 如果是相對路徑，相對於專案根目錄
            if not img_path.is_absolute():
                img_path = project_root / img_path

            if img_path.exists():
                try:
                    loaded_skills.append({
                        'key': item.get('key'),
                        'image': PIL.Image.open(img_path)
                    })
                except Exception as e:
                    self.log(f"Error loading skill image {img_path}: {e}")
        
        return loaded_skills

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
        for skill_data in self.user_skills:
            skill_image = skill_data.get("image")
            skill_key = skill_data.get("key")
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
        # 當list有東西，而且楓之谷在前景，且沒有收到停止信號
        while self.__skills_list and self.is_maple_focus() and self.should_continue():
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
            self.sleep(random.uniform(*self.__gap_time))

    def move_by_grappling(self) -> None:
        if self.is_maple_focus() and random.random() < 0.1:
            self.press_and_wait("8", 2)
            self.sleep(random.uniform(*self.__gap_time))
            self.key_down("down")
            self.press("alt")
            self.key_up("down")

    def walk_the_map(self) -> None:
        """
        根據錄製的腳本來重播操作
        """
        # 機率小於5％再來跑圖
        if random.random() < 0.05 and self.is_maple_focus():
            self.log("開始使用紀錄的腳本")

            recorded_events = self.__loop_map.get(self.get_character_position())
            self.replay_script(recorded_events)

    @cached_property
    def stop_on_rune(self):
        return self.__settings.get("stop_when_rune_appears", False)

    @cached_property
    def stop_on_people(self):
        return self.__settings.get("stop_when_people_appears", False)

    def start(self) -> None:
        try:
            while self.should_continue():
                # 在楓之谷在前景的狀況下，
                if self.is_maple_focus() :

                    # 如果地圖上有符文，且設定開啟，才暫停
                    if self.stop_on_rune and self.has_rune():
                        self.log("地圖上有符文 (暫停中...)")
                        self.sleep(10)
                        continue # 跳過本次迴圈的後續動作

                    # 如果地圖上有其他人，且設定開啟，才暫停
                    if self.stop_on_people and self.has_other_players():
                        self.log("地圖上有其他人 (暫停中...)")
                        self.sleep(10)
                        continue # 跳過本次迴圈的後續動作

                    # 如果沒有觸發暫停條件，那就開始練功
                    self.find_ready_skill()
                    self.press_ready_skills()
                    self.move_by_pressing_up()
                    # self.walk_the_map()
                    self.sleep(1)

                else:
                    self.sleep(1)
            
            self.log("練功腳本已停止")

        except KeyboardInterrupt:
            self.log(f'腳本中止')


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = MapleGrind(Xiao)
        Maple.start()
