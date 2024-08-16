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


def move_to_right():
    if random.random() < 0.25:
        pydirectinput.press("up")
        return True
    return False


def move_to_left():
    if random.random() < 0.25:
        pydirectinput.press("up")
        return False
    return True


def move_mouse_and_click(image: str, confidence: float = 0.9):
    pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)


def move_mouse(image: str, confidence: float = 0.9):
    pyautogui.moveTo(pyautogui.locateOnScreen(image, confidence=confidence))
    time.sleep(0.1)
