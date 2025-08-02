import sys
import time
import pygetwindow as gw
from collections import deque
import pyautogui
import random
import pyscreeze
import PIL.Image
from XiaoController import XiaoController
import os


class MapleScript:

    def __init__(self, controller=None):
        self.maple = self.get_maple()
        self.maple_full_screen_area = self._get_maple_full_screen_area()
        self.maple_skill_area = self._get_maple_skill_area()
        self.skills_queue = deque()
        self.gap_time = (0.5, 1.5)
        self.cur_dir = os.getcwd()
        self.keyboard = controller
        self.mouse = controller
        self.skills_dict = {
            # 漩渦球球
            "ball": {
                "key": "pagedown",
                "image": PIL.Image.open("photos/vortex_sphere.png"),
            },
            # 艾爾達斯降臨
            "erdas": {
                "key": "shift",
                "image": PIL.Image.open("photos/erda_shower.png"),
            },
            # 風轉奇想
            "wind": {
                "key": "end",
                "image": PIL.Image.open("photos/merciless_wind.png"),
            },
            # 小雞
            "chicken": {
                "key": "'",
                "image": PIL.Image.open("photos/phalanx_charge.png"),
            },
            # 龍捲風
            "tornado": {
                "key": "d",
                "image": PIL.Image.open("photos/howling_gale.png"),
            },
            # 季風
            "monsoon": {
                "key": "b",
                "image": PIL.Image.open("photos/monsoon.png"),
            },
            # 蜘蛛之鏡
            "spider": {
                "key": "f",
                "image": PIL.Image.open("photos/true_arachnid_reflection.png"),
            },
            # 烈陽印記
            "sun": {
                "key": "f5",
                "image": PIL.Image.open("photos/solar_crest.png"),
            },
            # 西爾芙之壁
            "shield": {
                "key": "6",
                "image": PIL.Image.open("photos/gale_barrier.png"),
            },
            # 武公
            "mu_gong": {
                "key": "f2",
                "image": PIL.Image.open("photos/mu_gong.png"),
            },
            # 爆擊強化
            # "vicious": {"key": "f3", "image": PIL.Image.open("photos/vicious_shot.png")},
            # 暴風加護
            # "big_arrow": {"key": "f4", "image": PIL.Image.open("photos/storm_whim.png")},
            # 一鍵爆發（超越者西格諾斯的祝福+爆擊強化+暴風加護）
            "aio": {
                "key": "f1",
                "image": PIL.Image.open("photos/aio.png"),
            },
            # 阿涅摩依
            "Anemoi": {
                "key": "v",
                "image": PIL.Image.open("photos/anemoi.png"),
            }
        }

    @staticmethod
    def _get_window_area(window: gw.Win32Window):
        """
        這是一個計算視窗面積的輔助函式，專門給 max() 的 key 使用。
        """
        return window.width * window.height

    def get_maple(self):
        """
        切換到楓之谷的程式
        :return: 楓之谷程式
        """
        maplestory = gw.getWindowsWithTitle("Maplestory")
        # 在找不到的情況下，代表楓之谷沒開啟，直接結束腳本
        if not maplestory:
            print("找不到楓之谷的程式")
            sys.exit()
        # 如果回傳的視窗有兩個，代表有一個是遊戲本體，一個是聊天室，但是遊戲本體一定比聊天室還要大
        real_maple = max(maplestory, key=self._get_window_area)
        if not real_maple.isActive:
            real_maple.activate()
        return real_maple

    def is_maple_focus(self) -> bool:
        """
        根據楓之谷在不在前景決定回傳的bool值
        :return:
        """
        return self.maple.isActive

    def _get_maple_full_screen_area(self):
        """
        回傳楓之谷視窗在螢幕上的位置
        :return: tuple
        """
        return self.maple.left, self.maple.top, self.maple.width, self.maple.height

    def get_full_screen_screenshot(self):
        return pyautogui.screenshot(region=self.maple_full_screen_area)

    def _get_maple_skill_area(self):
        # 只要看右下角就好
        left, top, width, height = self.maple_full_screen_area
        return left+ width // 2, top + height // 2, width // 2, height // 2

    def get_skill_area_screenshot(self):
        return pyautogui.screenshot(region=self.maple_skill_area)

    @staticmethod
    def is_on_screen(skill: PIL.Image.Image, img) -> bool:
        try:
            skill_location = next(pyautogui.locateAll(skill, img, confidence=0.96), None)
            return bool(skill_location)
        except pyscreeze.ImageNotFoundException:
            return False

    def find_and_click_image(self, pic_for_search: str | PIL.Image.Image) -> None:
        """
        用於辨識按鈕之後移動
        :param pic_for_search: 要辨識的圖片
        :return: None
        """
        try:
            # 取得目前滑鼠位置
            current_mouse_location = pyautogui.position()
            # 辨識遊戲截圖內有沒有我們要的東西
            picture_location = pyautogui.locateCenterOnScreen(pic_for_search, confidence=0.9)
            # 如果有辨識到東西
            if picture_location is not None:
                # 計算目前滑鼠的相對位置
                dx = int(picture_location.x - current_mouse_location[0])
                dy = int(picture_location.y - current_mouse_location[1])
                # 移動過去
                self.move((dx, dy))
                time.sleep(0.1)
                # 點下
                self.click()
            # 如果沒辨識到東西就不做任何事情
            else:
                print(f'畫面中找不到{pic_for_search}')
                pass
        except pyscreeze.ImageNotFoundException:
            print(f'畫面中找不到{pic_for_search}')
            # 如果沒辨識到東西就不做任何事情
            pass

    def find_ready_skill(self):
        """
        根據有沒有找到來決定要放哪個技能
        - 如果楓之谷不在前景，那麼就返回None
        - 如果楓之谷在前景，那麼就進行辨識
        :return: deque with all the key on the keyboard
        """
        # 先將序列清空，避免意外
        self.skills_queue.clear()

        # 如果楓之谷不在前景，那麼就返回None
        if not self.is_maple_focus():
            return None

        # 先截一次圖，判斷各個技能準備好了沒，並根據技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個queue當中
        screenshot = self.get_skill_area_screenshot()
        for skill_info in self.skills_dict.values():
            skill_image = skill_info.get("image")
            skill_key = skill_info.get("key")
            if self.is_on_screen(skill_image, screenshot):
                self.skills_queue.append(skill_key)

        # 用shuffle以增加隨機性
        random.shuffle(self.skills_queue)
        return None

    def press(self, key: str):
        self.keyboard.press_key(key)

    def move(self, location: tuple):
        self.mouse.send_mouse_location(location)

    def click(self):
        self.mouse.click()

    def press_ready_skills(self):
        """
        將技能一個一個按下去
        如果楓之谷不在前景，那麼就會清空
        :return:
        """
        # 如果queue是空的，就跳過所有步驟
        if not self.skills_queue:
            return None
        while self.skills_queue:
            # queue有東西但是楓之谷不在前景，那就直接清空之後跳過
            if not self.is_maple_focus():
                self.skills_queue.clear()
                break
            else:
                # 將按鍵一個一個按下
                key = self.skills_queue.pop()
                self.press(key)
                time.sleep(random.uniform(*self.gap_time))
                self.move_by_pressing_up()
        return None

    def move_by_pressing_up(self):
        if self.is_maple_focus() and random.random() < 0.2:
            self.press("up")

    def prepare_character(self):
        hamburger_menu = PIL.Image.open(r"photos\hamburger_menu.png")
        screenshot = self.get_skill_area_screenshot()
        # 如果畫面上出現漢堡選單，那就是技能列表沒有展開
        if self.is_on_screen(hamburger_menu, screenshot):
            # 展開技能列表
            self.press("]")

    def start(self):
        self.prepare_character()
        while True:
            if self.is_maple_focus():
                self.find_ready_skill()
                self.press_ready_skills()
                time.sleep(1)
            else:
                time.sleep(2)
                continue


if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = MapleScript(controller)
        Maple.start()
