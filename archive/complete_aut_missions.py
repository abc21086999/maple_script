from archive.functions import *


# 自動完成AUT的任務
def aut_main():
    # 切換到楓之谷的程式
    switch_to_maple()
    move_mouse_and_click('photos/schedule.png')
    move_mouse_and_click('photos/schedule_daily_all_complete.png')
    move_mouse_and_click('photos/schedule_panel_confirm.png')
    time.sleep(0.3)


if __name__ == "__main__":
    aut_main()
