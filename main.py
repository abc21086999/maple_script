from functions import *
from collections import deque
import random


# 切換到楓之谷的程式
switch_to_maple()

# 根據有沒有找到來決定要放哪個技能
def main():
    character = False
    queue = deque()
    # 創建一個嵌套字典，用於儲存各個技能有沒有準備好了
    skill_ready = {
        # 漩渦球球
        "ball": {"key": "pagedown", "photo_path": "photos/vortex_sphere.png"},
        # 艾爾達斯降臨
        "erdas": {"key": "shift", "photo_path": "photos/erda_shower.png"},
        # 風轉奇想
        "wind": {"key": "end", "photo_path": "photos/merciless_wind.png"},
        # 小雞
        "chicken": {"key": "'", "photo_path": "photos/phalanx_charge.png"},
        # 龍捲風
        "tornado": {"key": "d", "photo_path": "photos/howling_gale.png"},
        # 季風
        "monsoon": {"key": "b", "photo_path": "photos/monsoon.png"},
        # 蜘蛛之鏡
        "spider": {"key": "f", "photo_path": "photos/true_arachnid_reflection.png"},
        # 烈陽印記
        "sun": {"key": "f5", "photo_path": "photos/solar_crest.png"},
        # 西爾芙之壁
        "shield": {"key": "6", "photo_path": "photos/gale_barrier.png"},
        # 武公
        "mu_gong": {"key": "f2", "photo_path": "photos/mu_gong.png"},
        # 爆擊強化
        "vicious": {"key": "f3", "photo_path": "photos/vicious_shot.png"},
        # 暴風加護
        "big_arrow": {"key": "f4", "photo_path": "photos/storm_whim.png"},
    }

    while True:
        # 判斷各個技能準備好了沒，並根據技能準備好了沒的狀況，將準備好的技能的按鍵，加入一個queue當中
        for skill_info in skill_ready.values():
            if is_ready(skill_info.get("photo_path")):
                queue.append(skill_info.get("key"))

        random.shuffle(queue)

        # 一個一個將queue當中的東西取出並且按下去
        for i in range(len(queue)):
            pydirectinput.press(queue.popleft())
            # 讓按技能的間隔時間可以隨機
            time.sleep(random.uniform(0.1, 5.0))

        # 一個隨機按下上，來利用傳點移動的功能
        if not character:
            move_by_pressing_up()

        # 一個用繩索和下跳來隨機移動的功能
        # if not character and random.random() < 0.1 and is_ready("photos/grappling.png"):
        #     move_up_by_grappling()
        #     character = True
        # elif character and random.random() < 0.25:
        #     move_down_by_down_and_jump()
        #     character = False

        # 如果蒐藏到怪物那就停下來
        if is_ready("photos/monster_collected.png"):
            print("已收藏到怪物")
            break


if __name__ == "__main__":
    main()
