from functions import *


def main():
    # 切換到楓之谷的程式
    switch_to_maple()

    while True:
        queue = skill_ready()
        press_ready_skill(queue, min_sec=0.1, max_sec=1)
        move_by_pressing_up()
        if monster_collected():
            break


if __name__ == "__main__":
    main()
