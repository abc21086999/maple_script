import pyautogui
import time
import pydirectinput
import random
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


def move_by_pressing_up():
    if random.random() < 0.25:
        pydirectinput.press("up")


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
