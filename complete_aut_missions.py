from functions import *
from collections import deque
import random
import pydirectinput
import pyautogui


# 切換到楓之谷的程式
switch_to_maple()


# 根據有沒有找到來決定要放哪個技能
def main():
    while True:
        move_mouse("photos/name.png")
        move_mouse_and_click("photos/light_bulb.png")
        if is_ready("photos/complete.png"):
            for i in range(3):
                if is_ready("photos/next.png"):
                    pydirectinput.press("y")
            for i in range(3):
                if is_ready("photos/yes.png"):
                    move_mouse_and_click("photos/yes.png")
        else:
            break
#    點黃色燈泡
#    按下任務
#    再按一次
#    尋找是的位置，然後將滑鼠移動過去
#    點下去
#    重複一次


if __name__ == "__main__":
    main()
