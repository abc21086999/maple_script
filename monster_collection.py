from functions import *
from collections import deque
import random
import pydirectinput
import pyautogui


# 切換到楓之谷的程式
switch_to_maple()


# 根據有沒有找到來決定要放哪個技能
def monster_main():
    move_mouse_and_click("photos/hamburger_menu.png")
    move_mouse_and_click("photos/monster_collection.png", confidence=0.6)
    move_mouse_and_click("photos/adventure_tab.png")
    for i in range(5):
        move_mouse_and_click("photos/receive_monster_collection_reward.png")
        time.sleep(0.3)
        pydirectinput.press("enter")
    for i in range(5):
        move_mouse_and_click("photos/start_adventure.png")
        move_mouse_and_click("photos/confirm.png")
        move_mouse_and_click("photos/monster_collention_title.png")
    pydirectinput.press("esc")


if __name__ == "__main__":
    monster_main()
