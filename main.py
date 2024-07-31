import time
import pydirectinput
import pyautogui
from functions import is_ready
from collections import deque


# 切換到楓之谷的程式
pyautogui.moveTo(pyautogui.locateOnScreen("photos/maple.png", confidence=0.8))
pyautogui.click()
time.sleep(1)


# 根據有沒有找到來決定要放哪個技能
def main():
    queue = deque()
    # 創建一個嵌套字典，用於儲存各個技能有沒有準備好了
    skill_ready = {
        # 漩渦球球
        "ball": {"bool": False, "key": "pagedown", "photo_path": "photos/vortex_sphere.png"},
        # 艾爾達斯降臨
        "erdas": {"bool": False, "key": "shift", "photo_path": "photos/erda_shower.png"},
        # 風轉奇想
        "wind": {"bool": False, "key": "end", "photo_path": "photos/merciless_wind.png"},
        # 小雞
        "chicken": {"bool": False, "key": "'", "photo_path": "photos/phalanx_charge.png"},
        # 龍捲風
        "tornado": {"bool": False, "key": "d", "photo_path": "photos/howling_gale.png"},
        # 季風
        "monsoon": {"bool": False, "key": "b", "photo_path": "photos/monsoon.png"},
        # 蜘蛛之鏡
        "spider": {"bool": False, "key": "f", "photo_path": "photos/true_arachnid_reflection.png"},
        # 烈陽印記
        "sun": {"bool": False, "key": "f5", "photo_path": "photos/solar_crest.png"},
        # 西爾芙之壁
        "shield": {"bool": False, "key": "6", "photo_path": "photos/gale_barrier.png"},
        # 武公
        "mu_gong": {"bool": False, "key": "f2", "photo_path": "photos/mu_gong.png"},
        # 爆擊強化
        "vicious": {"bool": False, "key": "f3", "photo_path": "photos/vicious_shot.png"},
        # 暴風加護
        "big_arrow": {"bool": False, "key": "f4", "photo_path": "photos/storm_whim.png"},
    }

    while True:
        # 判斷各個技能準備好了沒
        for skill_info in skill_ready.values():
            skill_info["bool"] = is_ready(skill_info.get("photo_path"))

        # 根據各個技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個queue當中
        for key, sub_dict in skill_ready.items():
            if sub_dict.get("bool"):
                queue.append(sub_dict.get("key"))

        # 一個一個將queue當中的東西取出並且按下去
        for i in range(len(queue)):
            pydirectinput.press(queue.popleft())
            time.sleep(2)


if __name__ == "__main__":
    main()
