from src.utils.xiao_controller import XiaoController
from src.MapleScript import MapleScript
from src.utils.rune_detector import RuneDetector
from functools import cached_property
from pathlib import Path
import PIL.Image
import random
import time
from dataclasses import dataclass
from src.MapleMachine import Machine


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
        從 settings 讀取使用者自定義的練功技能，並載入圖片。
        支援舊版 list[dict] 相容與新版 dict 預設組格式。
        使用 cached_property 確保只載入一次。
        Returns:
            list[Skill]: [Skill(key="a", image=PIL.Image), ...]
        """
        # 1. 取得純資料
        raw_skills = self.settings.get('grind_skills', default=[])
        
        if isinstance(raw_skills, list):
            target_skills = raw_skills
        elif isinstance(raw_skills, dict):
            active_preset = str(raw_skills.get('active_preset', 0))
            presets = raw_skills.get('presets', {})
            target_skills = presets.get(active_preset, [])
        else:
            target_skills = []

        if not isinstance(target_skills, list):
            return []

        loaded_skills = []

        for item in target_skills:
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

    def solve_rune_encapsulation(self) -> None:
        """
        將解除輪迴的動作封裝起來。
        :return: None
        """
        if self.should_continue():
            if self.is_auto_solve_rune_enabled and self.has_rune():
                # 紀錄目前位置
                origin = self.get_player_pos()

                # 先移動到符文所在地
                if self.go_to_rune():
                    self.solve_rune()

                    # 如果有紀錄到原位置，就回去
                    if origin:
                        self.go_back(*origin)

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

        # 先按下一次對話鍵
        self.press("y")

        # 嘗試20次去辨識輪區域的邊框
        for i in range(20):
            results = []
            if not self.should_continue() or not self.is_maple_focus():
                return

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

    def up_jump(self):
        """
        模擬向上跳躍：依據設定動態選擇『上跳技能』或『上跳組合』
        """
        if not self.is_maple_focus():
            return

        jk = self.jump_key

        # 如果有設定上跳技能
        if self.is_up_jump_skill_enabled:
            self.press(self.up_jump_skill_key)
            self.sleep(0.3)

        # 如果是一般的上跳組合
        elif self.is_up_jump_combo_enabled:

            if self.up_jump_combo == "跳+上+跳":
                self.press(jk)
                self.sleep(0.1)
                self.key_down("up")
                self.key_down(jk)
                self.sleep(0.5)
                self.key_up(jk)
                self.key_up("up")
                self.sleep(0.3)

            elif self.up_jump_combo == "跳+上+上":
                self.press(jk)
                self.sleep(0.1)
                self.press("up")
                self.sleep(0.05)
                self.press("up")
                self.sleep(0.3)
        else:
            # 未勾選時的預設上跳行為 (跳 + 上 + 跳)
            self.press(jk)
            self.sleep(0.1)
            self.key_down("up")
            self.key_down(jk)
            self.sleep(0.5)
            self.key_up(jk)
            self.key_up("up")
            self.sleep(0.3)

    def down_jump(self):
        """
        模擬向下跳躍 (Down + 跳躍鍵)
        """
        if self.is_maple_focus():
            jk = self.jump_key
            self.key_down("down")
            self.press(jk)
            self.sleep(0.1)
            self.key_up("down")
            self.sleep(0.5)

    def move_to_point(self, target_x: int, target_y: int, threshold: int = 3):
        """
        導航至小地圖上的特定座標
        """
        self.log(f"開始導航至目標座標")

        current_dir = None  # 紀錄硬體目前的物理狀態 (None, "left", "right")

        # 定義一個內部的同步函數，只在狀態改變時發送指令
        def sync_hardware(new_dir):
            nonlocal current_dir
            if new_dir == current_dir:
                return  # 狀態沒變，不發指令，不浪費時間

            # 狀態改變了，先確保之前的方向鍵放開
            if current_dir:
                self.key_up(current_dir)

            # 再按下新的方向鍵
            if new_dir:
                self.key_down(new_dir)

            current_dir = new_dir  # 更新記憶狀態

        # 一個用於脫困用的函數
        def escape():
            nonlocal current_dir
            if current_dir:
                self.key_up(current_dir)
                self.sleep(0.1)
                self.key_down("down")
                self.sleep(3)
                self.key_up("down")
                self.sleep(0.1)
                self.key_down(current_dir)

        try:
            is_stuck_counter = 0
            last_position = None
            while self.should_continue() and self.is_maple_focus():
                curr = self.get_player_pos()
                if not curr:
                    self.log("找不到玩家位置，等待中...")
                    self.sleep(0.5)
                    continue

                cx, cy = curr
                dx = target_x - cx
                dy = target_y - cy

                # 判斷是否抵達目標 (水平與垂直都到位)
                if abs(dx) <= threshold and abs(dy) <= threshold:
                    self.log("已抵達目標點")
                    break

                # --- 決定理想的方向 (拆解寫法，一目瞭然) ---
                if dx > threshold:
                    target_dir = "right"
                elif dx < -threshold:
                    target_dir = "left"
                else:
                    target_dir = None

                # --- 同步硬體狀態 (只在方向改變時發指令) ---
                sync_hardware(target_dir)

                # 處理垂直移動 (這部分會與水平同時進行)
                # 只有在接近目標 X 座標時才處理 Y，避免因為地形跳過頭
                if abs(dx) <= threshold * 3:
                    if dy < -threshold:  # 目標在上方
                        self.up_jump()
                    elif dy > threshold:  # 目標在下方
                        self.down_jump()

                # 迴圈頻率穩定維持 20fps (0.05s)
                # 因為 sync_hardware 絕大部分時間會 return，所以迴圈反應極快
                self.sleep(0.05)

                # 如果角色位置都沒有改變，那麼就是卡住了
                # 增加一個卡住計數器
                if last_position is not None:
                    if last_position == curr:
                        is_stuck_counter += 1

                    # 如果位置不同，那就清空計數器
                    else:
                        is_stuck_counter = 0

                last_position = curr

                # 計數器數量多到一定程度代表玩家卡住了，就執行脫困，然後清空計數器
                if is_stuck_counter >= 40:
                    self.log(f'偵測到玩家卡在繩子上，將離開繩子')
                    escape()
                    is_stuck_counter = 0
                    last_position = None

        finally:
            # 確保退出時同步為停止狀態，並釋放所有可能的按鍵
            sync_hardware(None)
            self.release_all()

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

    @cached_property
    def is_wander_hold_key_enabled(self) -> bool:
        """隨機跑圖時是否長壓指定按鍵"""
        return self.__settings.get("enable_wander_hold_key", False)

    @cached_property
    def wander_hold_key(self) -> str:
        """隨機跑圖長壓的按鍵名稱"""
        return self.__settings.get("wander_hold_key", "shift")

    @cached_property
    def is_up_jump_combo_enabled(self) -> bool:
        """是否啟用上跳組合"""
        return self.__settings.get("enable_up_jump_combo", False)

    @cached_property
    def up_jump_combo(self) -> str:
        """上跳組合類型 ('跳+上+跳' 或 '跳+上+上')"""
        return self.__settings.get("up_jump_combo", "跳+上+跳")

    @cached_property
    def is_jump_key_enabled(self) -> bool:
        """是否指定跳躍按鍵"""
        return self.__settings.get("enable_jump_key", True)

    @cached_property
    def jump_key(self) -> str:
        """跳躍按鍵名稱 (若未啟用指定跳躍按鍵，預設回退為 'alt')"""
        if not self.is_jump_key_enabled:
            return "alt"
        return self.__settings.get("jump_key", "alt")

    @cached_property
    def is_up_jump_skill_enabled(self) -> bool:
        """是否啟用上跳技能"""
        return self.__settings.get("enable_up_jump_skill", False)

    @cached_property
    def up_jump_skill_key(self) -> str:
        """上跳技能按鍵名稱 (預設 'c')"""
        return self.__settings.get("up_jump_skill_key", "c")

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
        hold_key = self.wander_hold_key if self.is_wander_hold_key_enabled else None
        key_held = False

        def sync_dir(new_dir):
            nonlocal last_dir, key_held
            if new_dir == last_dir:
                return
            # 轉向時若有按住技能鍵，先放開以便轉向後重新補壓
            if hold_key and key_held:
                self.key_up(hold_key)
                key_held = False
                self.sleep(0.1)
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
                    continue
                
                cx, cy = curr
                
                # 邊界轉向判定 (20px 緩衝)
                if cx <= 20:
                    current_dir = "right"
                elif cx >= mw - 20:
                    current_dir = "left"
                
                # 執行移動
                sync_dir(current_dir)

                if hold_key and not key_held:
                    self.key_down(hold_key)
                    key_held = True
                
                # 10% 機率隨機跳躍，根據高度位置調整權重 (8:2)
                if random.random() < 0.1:
                    if cy > h_mid:
                        # 在下面，優先往上跳
                        jump_action = random.choices([self.up_jump, self.down_jump], weights=[80, 20])[0]
                    else:
                        # 在上面，優先往下跳
                        jump_action = random.choices([self.up_jump, self.down_jump], weights=[20, 80])[0]
                    
                    # 跳躍前若有按住技能鍵，先放開以避免跳躍動作被阻擋，落地後會自動補壓
                    if hold_key and key_held:
                        self.key_up(hold_key)
                        key_held = False
                        self.sleep(0.1)

                    jump_action()

                    if hold_key and not key_held:
                        self.key_down(hold_key)
                        key_held = True

                self.sleep(0.1)
        finally:
            sync_dir(None) # 停止移動
            self.release_all()
            self.go_back(*origin)

        # 回歸後自動面向中心
        if self.is_face_center_enabled:
            self.face_center()

    def start(self) -> None:
        try:
            while self.should_continue() and (self.is_stationary or self.is_route_enabled or self.is_random_wander_enabled):

                state_machine = Machine(self)
                state_machine.run()

            self.log("練功腳本已停止")

        except KeyboardInterrupt:
            self.log(f'腳本中止')

        finally:
            self.release_all()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = MapleGrind(Xiao)
        Maple.start()
