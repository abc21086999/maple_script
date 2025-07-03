from functions import *


def main():
    # 切換到楓之谷的程式
    maple = switch_to_maple()

    while True:
        if maple.isActive:
            queue = skill_ready(maple)
            press_ready_skill(maple, queue, min_sec=0.1, max_sec=1)
            move_by_pressing_up()
        else:
            continue


if __name__ == "__main__":
    main()
