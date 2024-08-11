import pyautogui
import time
import pydirectinput
import random


def is_ready(skill: str):
    try:
        if pyautogui.locateOnScreen(skill, confidence=0.96):
            return True
    except pyautogui.ImageNotFoundException:
        return False


def switch_to_maple():
    while True:
        try:
            pyautogui.moveTo(pyautogui.locateOnScreen("photos/maple.png", confidence=0.8))
            pyautogui.click()
            time.sleep(1)
            break
        except pyautogui.ImageNotFoundException:
            print("沒有看到楓之谷的程式")
            time.sleep(5)


def jump_to_right():
    if random.random() < 0.2:
        pydirectinput.press(keys=["alt", "space", "space", "space", "space", "space", "space", "space", "space",
                                  "space", "space", "space", "space", "space"], interval=0.6)
        pydirectinput.press("right")
        pydirectinput.press("left")
        return True
    return False


def jump_to_left():
    if random.random() < 0.3:
        pydirectinput.press(keys=["alt", "space", "space", "space", "space", "space", "space", "space", "space",
                                  "space", "space", "space", "space", "space"], interval=0.6)
        pydirectinput.press("right")
        return False
    return True
