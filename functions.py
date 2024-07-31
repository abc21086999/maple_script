import pyautogui


def is_ready(skill: str):
    try:
        if pyautogui.locateOnScreen(skill, confidence=0.96):
            return True
    except pyautogui.ImageNotFoundException:
        return False
