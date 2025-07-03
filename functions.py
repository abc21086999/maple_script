import pyautogui
import time
import pydirectinput
import random
from collections import deque
from pyautogui import ImageNotFoundException
import pygetwindow as gw


def is_ready(skill: str, region: tuple) -> bool:
    try:
        if pyautogui.locateOnScreen(skill, region=region, confidence=0.96):
            return True
        return False
    except pyautogui.PyAutoGUIException:
        return False


def press_and_wait(key: str, wait_time : float | int = 0):
    pydirectinput.press(key)
    if wait_time:
        time.sleep(wait_time)


def get_window_area(window):
    """這是一個計算視窗面積的輔助函式，專門給 max() 的 key 使用。"""
    return window.width * window.height


def switch_to_maple():
    """
    切換到楓之谷的程式
    :return: 楓之谷程式
    """
    maplestory = gw.getWindowsWithTitle("Maplestory")
    # 如果回傳的視窗有兩個，代表有一個是遊戲本體，一個是聊天室，但是遊戲本體一定比聊天室還要大
    if isinstance(maplestory, list):
        real_maple = max(maplestory, key=get_window_area)
    else:
        real_maple = maplestory
    if not real_maple.isActive:
        real_maple.activate()
    return real_maple


def skill_ready(maple: gw.Win32Window) -> deque:
    """
    根據有沒有找到來決定要放哪個技能
    - 如果楓之谷不在前景，那麼就返回空的序列
    - 如果楓之谷在前景，那麼就進行辨識
    :return: deque with all the key on the keyboard
    """
    queue = deque()
    # 如果楓之谷不在前景，那麼就返回空的序列
    if not maple.isActive:
        return queue
    # 楓之谷的視窗位置
    maple_window_area = (maple.left, maple.top, maple.width, maple.height)
    # 創建一個嵌套字典，用於儲存各個技能有沒有準備好了
    skill_dict = {
        # 漩渦球球
        "ball": {"key": "pagedown", "photo_path": "photos/vortex_sphere.png"},
        # 艾爾達斯降臨
        "erdas": {"key": "shift", "photo_path": "photos/erda_shower.png"},
        # 風轉奇想
        "wind": {"key": "end", "photo_path": "photos/merciless_wind.png"},
        # 小雞
        "chicken": {"key": "'", "photo_path": "photos/phalanx_charge.png"},
        # 龍捲風
        "tornado": {"key": "d", "photo_path": "photos/howling_gale.png"},
        # 季風
        "monsoon": {"key": "b", "photo_path": "photos/monsoon.png"},
        # 蜘蛛之鏡
        "spider": {"key": "f", "photo_path": "photos/true_arachnid_reflection.png"},
        # 烈陽印記
        "sun": {"key": "f5", "photo_path": "photos/solar_crest.png"},
        # 西爾芙之壁
        "shield": {"key": "6", "photo_path": "photos/gale_barrier.png"},
        # 武公
        "mu_gong": {"key": "f2", "photo_path": "photos/mu_gong.png"},
        # 爆擊強化
        # "vicious": {"key": "f3", "photo_path": "photos/vicious_shot.png"},
        # 暴風加護
        # "big_arrow": {"key": "f4", "photo_path": "photos/storm_whim.png"},
        # 一鍵爆發（超越者西格諾斯的祝福+爆擊強化+暴風加護）
        "aio": {"key": "f1", "photo_path": "photos/aio.png"},
        # 阿涅摩依
        "Anemoi": {"key": "v", "photo_path": "photos/anemoi.png"}
    }
    # 判斷各個技能準備好了沒，並根據技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個queue當中
    for skill_info in skill_dict.values():
        if is_ready(skill_info.get("photo_path"), region=maple_window_area):
            queue.append(skill_info.get("key"))
    # 用shuffle以增加隨機性
    random.shuffle(queue)
    return queue


def press_ready_skill(maple, queue: deque, min_sec : float | int = 0.1, max_sec : float | int = 3.0):
    # 一個一個將queue當中的東西取出並且按下去
    if len(queue) == 0:
        return None
    while queue:
        if not maple.isActive:
            queue.popleft()
            continue
        pydirectinput.press(queue.popleft())
        # 讓按技能的間隔時間可以隨機
        time.sleep(random.uniform(min_sec, max_sec))
    return None


def move_by_pressing_up(probability: float = 0.2):
    # 一個隨機按下上，來利用傳點移動的功能
    if random.random() < probability:
        pydirectinput.press("up")
    # if random.random() < probability and is_ready("photos/blink.png"):
    #     pydirectinput.press("pageup")


def monster_collected() -> bool:
    # 如果蒐藏到怪物那就停下來
    if is_ready("photos/monster_collected.png"):
        print("已收藏到怪物")
        return True
    return False


def move_up_by_grappling():
    pydirectinput.press("8")


def move_down_by_down_and_jump():
    pydirectinput.keyDown("down")
    pydirectinput.press("alt")
    pydirectinput.keyUp("down")


def move_mouse_and_click(image: str, confidence: float = 0.9, wait_time: float | int = 0):
    try:
        pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.1) if not wait_time else time.sleep(wait_time)
    except ImageNotFoundException:
        print(f'找不到{image}')


def move_mouse(image: str, confidence: float = 0.9, wait_time: float | int = 0):
    if confidence > 1 or confidence < 0:
        return None
    try:
        pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
        time.sleep(0.1) if not wait_time else time.sleep(wait_time)
        return None
    except ImageNotFoundException:
        print(f'找不到{image}')
        return None


def move_up_by_up_and_jump():
    pydirectinput.keyDown("alt")
    pydirectinput.keyDown("up")
    pydirectinput.keyUp("alt")
    pydirectinput.keyDown("alt")
    pydirectinput.keyUp("alt")
    pydirectinput.keyUp("up")


def decide_set():
    move_mouse_and_click('photos/character_icon.png')
    move_mouse_and_click('photos/character_setting.png')
    # 練功沒亮著代表裝備沒有切換到練功用的設定
    if is_ready('photos/daily_set.png'):
        move_mouse_and_click('photos/daily_set.png')
        move_mouse_and_click('photos/daily_apply.png')
        move_mouse_and_click('photos/confirm.png', confidence=0.7)
        print("預設套組已經準備好練功")
    # 練功亮著代表可能是在練功的設定，但也有可能是裝備切換到了但是其他東西還沒切換
    else:
        move_mouse_and_click('photos/daily_apply.png')
        # 有某個東西沒有切換到，才會跳出需要按下確認按鈕
        if is_ready('photos/confirm.png'):
            move_mouse_and_click('photos/confirm.png', confidence=0.7)
        else:
            print("預設套組已經準備好練功")
    press_and_wait("esc", 0.3)
    press_and_wait("=", 0.5)


def battle_union_coin():
    move_mouse_and_click('photos/hamburger_menu.png')
    time.sleep(0.3)
    move_mouse_and_click('photos/battle_union.png')
    time.sleep(1)
    move_mouse('photos/artifact.png')
    time.sleep(1)
    move_mouse_and_click('photos/get_coin.png')
    for i in range(2):
        pydirectinput.press("esc")


def start_daily_missions():
    move_mouse_and_click('photos/daily_schedule.png', wait_time=0.2)
    move_mouse_and_click('photos/schedule_daily_all_start.png', wait_time=0.2)
    press_and_wait("esc", 0.2)

def go_to_village():
    """
    去到技術村
    :return: None
    """
    move_mouse_and_click('photos/fast_travel.png')
    move_mouse_and_click('photos/village.png')
    press_and_wait("right", 0.3)
    press_and_wait("enter", 3)

def disassemble_armor():
    """
    自動選擇分解裝備，跟具有沒有裝備放到面板上決定分解好了沒
    :return: None
    """
    press_and_wait("i", 0.5)
    move_mouse_and_click('photos/disassemble_panel.png', wait_time=0.5)
    move_mouse_and_click('photos/put_all_armor_on_table.png', wait_time=0.3)
    move_mouse('photos/name.png', wait_time=0.3)
    while True:
        if not is_ready('photos/empty_disassembly_table.png'):
            print("有裝備可以分解")
            move_mouse_and_click('photos/disassemble.png', wait_time=0.3)
            press_and_wait("enter", 3)
            press_and_wait("enter", 0.5)
            move_mouse_and_click('photos/put_all_armor_on_table.png', wait_time=0.3)
            move_mouse('photos/name.png', wait_time=0.2)
        else:
            print("沒裝備可以分解")
            for i in range(2):
                pydirectinput.press("esc")
            pydirectinput.press("up")
            break



# 一個用繩索和下跳來隨機移動的功能
# if not character and random.random() < 0.1 and is_ready("photos/grappling.png"):
#     move_up_by_grappling()
#     character = True
# elif character and random.random() < 0.25:
#     move_down_by_down_and_jump()
#     character = False


if __name__ == "__main__":
    pass
    # maplestory = gw.getWindowsWithTitle("Maplestory")
    # 如果回傳的視窗有兩個，代表有一個是遊戲本體，一個是聊天室
    # if isinstance(maplestory, list):
    #     first_maple_size = maplestory[0].width * maplestory[0].height
    #     second_maple_size = maplestory[1].width * maplestory[1].height
    #     real_maple = max(first_maple_size, second_maple_size)
    #     print(real_maple)