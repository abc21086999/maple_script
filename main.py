import time
import pydirectinput
import pyautogui
import cv2
import numpy as np
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
        "ball": {"bool": False, "key": "pagedown"},
        "erdas": {"bool": False, "key": "shift"},
        "wind": {"bool": False, "key": "end"},
        "chicken": {"bool": False, "key": "'"},
        "tornado": {"bool": False, "key": "d"},
        "monsoon": {"bool": False, "key": "b"},
        "spider": {"bool": False, "key": "f"},
        "sun": {"bool": False, "key": "f5"},
        "shield": {"bool": False, "key": "6"},
        "mu_gong": {"bool": False, "key": "f2"},
        "vicious": {"bool": False, "key": "f3"},
        "big_arrow": {"bool": False, "key": "f4"},
    }

    while True:
        # 判斷漩渦球球
        try:
            if pyautogui.locateOnScreen("photos/vortex_sphere.png", confidence=0.96):
                skill_ready["ball"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["ball"]["bool"] = False

        # 判斷風轉奇想
        try:
            if pyautogui.locateOnScreen("photos/merciless_wind.png", confidence=0.96):
                skill_ready["wind"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["wind"]["bool"] = False

        # 判斷艾爾達斯降臨
        try:
            if pyautogui.locateOnScreen("photos/erda_shower.png", confidence=0.96):
                skill_ready["erdas"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["erdas"]["bool"] = False

        # 判斷小雞
        try:
            if pyautogui.locateOnScreen("photos/phalanx_charge.png", confidence=0.96):
                skill_ready["chicken"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["chicken"]["bool"] = False

        # 判斷龍捲風
        try:
            if pyautogui.locateOnScreen("photos/howling_gale.png", confidence=0.96):
                skill_ready["tornado"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["tornado"]["bool"] = False

        # 判斷季風
        try:
            if pyautogui.locateOnScreen("photos/monsoon.png", confidence=0.96):
                skill_ready["monsoon"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["monsoon"]["bool"] = False

        # 判斷蜘蛛之鏡
        try:
            if pyautogui.locateOnScreen("photos/true_arachnid_reflection.png", confidence=0.96):
                skill_ready["spider"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["spider"]["bool"] = False

        # 判斷烈陽印記
        try:
            if pyautogui.locateOnScreen("photos/solar_crest.png", confidence=0.96):
                skill_ready["sun"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["sun"]["bool"] = False

        # 判斷西爾芙之壁
        try:
            if pyautogui.locateOnScreen("photos/gale_barrier.png", confidence=0.96):
                skill_ready["shield"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["shield"]["bool"] = False

        # 判斷武公
        try:
            if pyautogui.locateOnScreen("photos/mu_gong.png", confidence=0.96):
                skill_ready["mu_gong"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["mu_gong"]["bool"] = False

        # 判斷爆擊強化
        try:
            if pyautogui.locateOnScreen("photos/vicious_shot.png", confidence=0.96):
                skill_ready["vicious"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["vicious"]["bool"] = False

        # 判斷暴風加護
        try:
            if pyautogui.locateOnScreen("photos/storm_whim.png", confidence=0.96):
                skill_ready["big_arrow"]["bool"] = True
        except pyautogui.ImageNotFoundException:
            skill_ready["big_arrow"]["bool"] = False

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
