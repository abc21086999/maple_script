import sys
from dotenv import load_dotenv
from src.MapleGrind import MapleGrind
from src.MonsterCollection import MonsterCollection
from src.DailyPrepare import DailyPrepare
from src.Storage import Storage
from src.XiaoController import XiaoController
from src.DailyBoss import DailyBoss
from src.DancingMachine import Dancing


task_mapping = {
    "grind": MapleGrind,
    "collection": MonsterCollection,
    "daily": DailyPrepare,
    "daily_boss": DailyBoss,
    "storage": Storage,
    "dance": Dancing,
}

def run():
    """
    應用程式主入口
    """
    if len(sys.argv) < 2:
        print("錯誤：請提供一個任務指令。")
        print("可用指令: grind, collection, daily, daily_boss, storage, dance")
        input("輸入任意鍵繼續...")
        return

    task = sys.argv[1]
    load_dotenv()

    with XiaoController() as xiao:
        if task in task_mapping:
            work = task_mapping.get(task)
            work(controller=xiao).start()
        else:
            print(f"未知的任務：{task}")
            input("輸入任意鍵繼續...")


if __name__ == "__main__":
    run()
