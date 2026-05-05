from src.utils.xiao_controller import XiaoController
from src.MapleScript import MapleScript
from src.utils.rune_detector import RuneDetector
from functools import cached_property
from pathlib import Path
import PIL.Image
import random
import time
from dataclasses import dataclass


@dataclass
class Skill:
    key: str
    image: PIL.Image.Image


class MapleGrind(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__skills_list = list()
        self.__gap_time = self.yaml_loader.grind_setting
        self.__settings = self.settings.get("grind_settings")

    @cached_property
    def user_skills(self) -> list[Skill]:
        """
        從 settings.yaml 讀取使用者自定義的練功技能，並載入圖片。
        使用 cached_property 確保只載入一次。
        Returns:
            list[Skill]: [Skill(key="a", image=PIL.Image), ...]
        """
        # 1. 取得純資料
        raw_skills = self.settings.get('grind_skills', default=[])
        
        if not isinstance(raw_skills, list):
            return []

        loaded_skills = []

        for item in raw_skills:
            # 必須啟用且有圖片路徑
            if not item.get('enabled', False) or not item.get('image_path'):
                continue

            path_str = item.get('image_path')
            img_path = Path(path_str)

            if img_path.exists():
                try:
                    loaded_skills.append(
                        Skill(
                            key = item.get('key'),
                            image = PIL.Image.open(img_path)
                        )
                    )
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
            skill_image = skill_data.image
            skill_key = skill_data.key
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

    def wait_until_safe(self) -> bool:
        """
        持續檢查直到環境安全 (焦點、符文、其他玩家)。
        :return: bool 如果回傳 False 代表收到了停止信號
        """
        while self.should_continue():
            if not self.is_maple_focus():
                self.log("楓之谷不在前景，暫停中")
                self.sleep(1)
                continue

            if self.is_auto_solve_rune_enabled and self.has_rune():
                # 紀錄目前位置
                origin = self.get_player_pos()

                # 先移動到符文所在地
                if self.go_to_rune():
                    self.solve_rune()

                    # 如果有紀錄到原位置，就回去
                    if origin:
                        self.go_back(*origin)

            if self.stop_on_rune and self.has_rune():
                self.log("地圖上有符文 (暫停中...)")
                self.sleep(10)
                continue

            if self.stop_on_people and self.has_other_players():
                self.log("地圖上有其他人 (暫停中...)")
                self.sleep(10)
                continue

            # 通過所有檢查
            return True
        return False

    def monitor_and_grind(self, seconds: float = 0):
        """
        在指定時間內監控安全並執行原地練功。
        :param seconds: 持續秒數。如果是 0，則只執行一輪檢查與練功。
        """
        end_time = time.time() + seconds

        while self.should_continue():
            # 1. 確保環境安全
            if not self.wait_until_safe():
                break

            # 2. 執行原地練功 (如果有開啟的話)
            if self.is_stationary:
                self.grind_mode()

            # 3. 判斷是否達成時間要求
            if seconds <= 0 or time.time() >= end_time:
                break

            # 4. 避免過於頻繁的循環
            self.sleep(1)

    def walk_the_map(self) -> None:
        """
        根據錄製的腳本來重播操作
        """
        if self.is_route_enabled:
            recorded_events = self.settings.get('recorded_route', default=[])

            if recorded_events:
                self.log("開始執行錄製的腳本")
                self.replay_script(recorded_events)
            else:
                self.log("警告: 未錄製任何路徑 (或路徑為空)")

            # 如果有設定間隔，就休息一下，進入原地練功；否則直接進行下一輪
            if self.is_loop_interval_enabled:
                self.log(f"腳本執行完畢，等待下一次循環: {self.route_interval_seconds} 秒")
                self.monitor_and_grind(self.route_interval_seconds)

    def grind_mode(self):
        """
        原地練功模式的封裝
        :return:
        """
        self.find_ready_skill()
        self.press_ready_skills()
        if self.is_random_up_enabled:
            self.move_by_pressing_up()

    def solve_rune(self):
        """
        解輪
        :return:
        """
        # 只在要用到的時候再初始化
        if self._model is None:
            self._model = RuneDetector()

        rune_edge = self.yaml_loader.rune_box_edge
        results = []

        # 先按下一次對話鍵
        self.press("y")

        # 嘗試20次去辨識輪區域的邊框
        for i in range(20):
            arrows = self._vision.get_rune_arrows(rune_edge)
            # 如果沒辨識到那就普攻幾次
            if arrows is None:
                for _ in range(3):
                    self.press_and_wait(self.normal_skill_key, 0.3)
                self.sleep(0.3)
                self.press_and_wait("y", 1)
                continue

            # 如果有辨識到，那麼就把每張圖片丟進去推論
            for arrow in arrows:
                direction, confidence = self._model.predict(arrow)
                results.append({"direction": direction, "confidence": confidence})

            # 只有在信心水準足夠的時候才按下按鍵
            if all(inference_result.get("confidence") > 0.8 for inference_result in results):
                for result in results:
                    self.press_and_wait(result.get("direction"), 0.2)
                self.log("地圖輪解除成功")
                return

        self.log("符文解除失敗")

    def go_to_rune(self) -> bool:
        """
        移動至符文位置
        :return: bool 是否成功移動到符文附近
        """
        rune_pos = self.get_rune_pos()
        if rune_pos:
            rx, ry = rune_pos
            self.log(f"開始前往符文座標: ({rx}, {ry})")
            self.move_to_point(rx, ry)
            self.sleep(1)  # 確保角色落地
            return True
        else:
            self.log("無法獲取符文在小地圖上的座標")
            return False

    def go_back(self, target_x: int, target_y: int):
        """
        返回指定的座標點 (通常是原練功點)
        """
        self.log(f"任務完成，返回原練功點")
        self.move_to_point(target_x, target_y)
        self.sleep(2)

    def face_center(self):
        """
        讓角色面向地圖中軸
        """
        curr = self.get_player_pos()
        if curr:
            cx, _ = curr
            _, _, mw, _ = self._vision.get_mini_map_area()
            if cx < mw / 2:
                # 在左邊，面向右
                self.press("right")
            else:
                # 在右邊，面向左
                self.press("left")

    @cached_property
    def is_stationary(self) -> bool:
        """是否為定點練功模式"""
        return self.__settings.get("stationary_mode", False)

    @cached_property
    def is_random_up_enabled(self) -> bool:
        return self.__settings.get("random_up_movement", False)

    @cached_property
    def is_route_enabled(self) -> bool:
        """是否啟用錄製的路徑"""
        return self.__settings.get("enable_loop_route", False)

    @cached_property
    def is_loop_interval_enabled(self) -> bool:
        """是否啟用循環間隔 (CD時間)"""
        return self.__settings.get("enable_loop_interval", False)

    @cached_property
    def route_interval_seconds(self) -> int:
        """循環間隔秒數"""
        return int(self.__settings.get("loop_route_interval", 5))

    @cached_property
    def stop_on_rune(self):
        return self.__settings.get("stop_when_rune_appears", False)

    @cached_property
    def stop_on_people(self):
        return self.__settings.get("stop_when_people_appears", False)

    @cached_property
    def is_auto_solve_rune_enabled(self) -> bool:
        """是否啟用自動解除地圖輪迴"""
        return self.__settings.get("auto_solve_rune", False)

    @cached_property
    def normal_skill_key(self) -> str:
        """從 normal_skills.json 讀取常用攻擊技能按鍵"""
        return self.settings.get("normal_skills", key="normal", default="a")

    @cached_property
    def is_random_wander_enabled(self) -> bool:
        """是否啟用隨機亂逛模式"""
        return self.__settings.get("enable_random_wander", False)

    @cached_property
    def is_face_center_enabled(self) -> bool:
        """結束後是否面向中心"""
        return self.__settings.get("face_center_after_wander", False)

    @cached_property
    def random_wander_duration(self) -> int:
        """隨機亂逛持續秒數"""
        return int(self.__settings.get("random_wander_duration", 30))

    @cached_property
    def is_random_wander_interval_enabled(self) -> bool:
        """是否啟用隨機跑圖的循環冷卻"""
        return self.__settings.get("enable_random_wander_interval", False)

    @cached_property
    def random_wander_interval_seconds(self) -> int:
        """隨機跑圖的循環冷卻秒數"""
        return int(self.__settings.get("random_wander_interval", 50))

    def random_wander(self):
        """
        在指定時間內隨機左右亂逛，靠近邊界 20px 自動轉向，最後回到原位。
        """
        if not self.is_random_wander_enabled:
            return

        origin = self.get_player_pos()
        if not origin:
            self.log("找不到玩家位置，取消隨機亂逛")
            return

        self.log(f"開始隨機亂逛，持續 {self.random_wander_duration} 秒")
        
        # 取得小地圖寬度與高度
        _, _, mw, mh = self._vision.get_mini_map_area()
        h_mid = mh / 2
        
        end_time = time.time() + self.random_wander_duration
        current_dir = random.choice(["left", "right"])
        
        # 同步硬體的輔助函數
        last_dir = None

        def sync_dir(new_dir):
            nonlocal last_dir
            if new_dir == last_dir:
                return
            if last_dir:
                self.key_up(last_dir)
            if new_dir:
                self.key_down(new_dir)
            last_dir = new_dir

        try:
            while self.should_continue() and time.time() < end_time and self.is_maple_focus():
                # 取得目前位置
                curr = self.get_player_pos()
                if not curr:
                    self.sleep(0.5)
                    continue
                
                cx, cy = curr
                
                # 邊界轉向判定 (20px 緩衝)
                if cx <= 20:
                    current_dir = "right"
                elif cx >= mw - 20:
                    current_dir = "left"
                
                # 執行移動
                sync_dir(current_dir)
                
                # 10% 機率隨機跳躍，根據高度位置調整權重 (8:2)
                if random.random() < 0.1:
                    if cy > h_mid:
                        # 在下面，優先往上跳
                        jump_action = random.choices([self.up_jump, self.down_jump], weights=[80, 20])[0]
                    else:
                        # 在上面，優先往下跳
                        jump_action = random.choices([self.up_jump, self.down_jump], weights=[20, 80])[0]
                    
                    jump_action()
                
                self.sleep(0.1)
        finally:
            sync_dir(None) # 停止移動
            self.go_back(*origin)

        # 回歸後自動面向中心
        if self.is_face_center_enabled:
            self.face_center()

        # 處理循環冷卻邏輯
        if self.is_random_wander_interval_enabled:
            self.log(f"隨機跑圖結束，等待下一次循環: {self.random_wander_interval_seconds} 秒")
            self.monitor_and_grind(self.random_wander_interval_seconds)

    def start(self) -> None:
        try:
            while self.should_continue() and (self.is_stationary or self.is_route_enabled or self.is_random_wander_enabled):
                # 1. 等待直到環境安全
                if not self.wait_until_safe():
                    break
                
                # 2. 執行原地練功
                self.monitor_and_grind(0)

                # 3. 執行路徑
                self.walk_the_map()

                # 4. 執行隨機亂逛
                self.random_wander()

                # 一個短暫的等待以避免空轉
                self.sleep(1)

            self.log("練功腳本已停止")

        except KeyboardInterrupt:
            self.log(f'腳本中止')


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = MapleGrind(Xiao)
        Maple.start()
