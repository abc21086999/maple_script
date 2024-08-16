from functions import *
from collections import deque
import random
import pydirectinput
import pyautogui


# 切換到楓之谷的程式
switch_to_maple()


# 完成怪物蒐藏並且重新開始探索
def monster_main():
    # 移動到漢堡選單
    move_mouse_and_click("photos/hamburger_menu.png")
    # 點擊怪物蒐藏
    move_mouse_and_click("photos/monster_collection.png", confidence=0.6)
    # 點擊探險那個tab
    move_mouse_and_click("photos/adventure_tab.png")
    for i in range(5):
        # 點擊完成蒐藏
        move_mouse_and_click("photos/receive_monster_collection_reward.png")
        time.sleep(0.3)
        pydirectinput.press("enter")
    for i in range(5):
        # 重新開始探險
        move_mouse_and_click("photos/start_adventure.png")
        move_mouse_and_click("photos/confirm.png")
        move_mouse_and_click("photos/monster_collention_title.png")
    # 完成後關閉視窗
    pydirectinput.press("esc")


if __name__ == "__main__":
    monster_main()
