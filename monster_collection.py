from functions import *
import pydirectinput


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
    time.sleep(0.3)
    while True:
        if is_ready("photos/receive_monster_collection_reward.png"):
                # 點擊完成蒐藏
                move_mouse_and_click("photos/receive_monster_collection_reward.png")
                time.sleep(0.3)
                pydirectinput.press("enter")
                # 重新開始探險
                move_mouse_and_click("photos/monster_collection_title.png")
                move_mouse_and_click("photos/start_adventure.png")
                move_mouse_and_click("photos/confirm.png")
                move_mouse_and_click("photos/monster_collection_title.png")
        else:
            # 完成後關閉視窗
            pydirectinput.press("esc")
            break


if __name__ == "__main__":
    monster_main()
