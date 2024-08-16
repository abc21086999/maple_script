from functions import *
import pydirectinput


# 切換到楓之谷的程式
switch_to_maple()


# 自動完成AUT的任務
def aut_main():
    while True:
        # 移動到角色ID作為緩衝
        move_mouse("photos/name.png")
        # 點擊黃色燈泡
        move_mouse_and_click("photos/light_bulb.png")
        # 如果有已經完成的任務
        if is_ready("photos/complete.png"):
            # 最多按三次Y
            for i in range(3):
                if is_ready("photos/next.png"):
                    pydirectinput.press("y")
            # 最多按三次『是』
            for i in range(3):
                if is_ready("photos/yes.png"):
                    move_mouse_and_click("photos/yes.png")
        # 沒有已經完成的任務，跳出迴圈
        else:
            break


if __name__ == "__main__":
    aut_main()
