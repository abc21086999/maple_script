import pyautogui
import time
import pydirectinput
import random
from collections import deque
from pyautogui import ImageNotFoundException


def is_ready(skill: str):
    try:
        if pyautogui.locateOnScreen(skill, confidence=0.96):
            return True
    except ImageNotFoundException:
        return False


def switch_to_maple():
    while True:
        try:
            pyautogui.moveTo(pyautogui.locateOnScreen("photos/maple.png", confidence=0.8))
            pyautogui.click()
            time.sleep(1)
            break
        except ImageNotFoundException:
            print("沒有看到楓之谷的程式")
            time.sleep(5)


def skill_ready() -> deque:
    """
    根據有沒有找到來決定要放哪個技能
    :return: deque with all the key on the keyboard
    """
    queue = deque()
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
        "vicious": {"key": "f3", "photo_path": "photos/vicious_shot.png"},
        # 暴風加護
        "big_arrow": {"key": "f4", "photo_path": "photos/storm_whim.png"},
    }
    # 判斷各個技能準備好了沒，並根據技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個queue當中
    for skill_info in skill_dict.values():
        if is_ready(skill_info.get("photo_path")):
            queue.append(skill_info.get("key"))
    # 用shuffle以增加隨機性
    random.shuffle(queue)
    return queue


def press_ready_skill(queue: deque, min_sec : float | int = 0.1, max_sec : float | int = 3.0):
    # 一個一個將queue當中的東西取出並且按下去
    for i in range(len(queue)):
        pydirectinput.press(queue.popleft())
        # 讓按技能的間隔時間可以隨機
        time.sleep(random.uniform(min_sec, max_sec))


def move_by_pressing_up(probability: float = 0.2):
    # 一個隨機按下上，來利用傳點移動的功能
    if random.random() < probability:
        pydirectinput.press("up")


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


def move_mouse_and_click(image: str, confidence: float = 0.9):
    try:
        pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.1)
    except ImageNotFoundException:
        print(f'找不到{image}')


def move_mouse(image: str, confidence: float = 0.9):
    try:
        pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
        time.sleep(0.1)
    except ImageNotFoundException:
        print(f'找不到{image}')

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
    pydirectinput.press("esc")




# 一個用繩索和下跳來隨機移動的功能
# if not character and random.random() < 0.1 and is_ready("photos/grappling.png"):
#     move_up_by_grappling()
#     character = True
# elif character and random.random() < 0.25:
#     move_down_by_down_and_jump()
#     character = False
