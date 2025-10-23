import sys
from src.MapleGrind import MapleGrind
from src.MonsterCollection import MonsterCollection
from src.DailyPrepare import DailyPrepare
from src.XiaoController import XiaoController

def run():
    """
    應用程式主入口
    """
    if len(sys.argv) < 2:
        print("錯誤：請提供一個任務指令。")
        print("可用指令: grind, collection, prepare")
        return

    task = sys.argv[1]

    # 使用 with 語句確保 XiaoController 能正確關閉
    with XiaoController() as xiao:
        if task == 'grind':
            print("正在啟動掛機模組...")
            grinder = MapleGrind(controller=xiao)
            grinder.start() # 假設主要執行方法是 start_grind
        elif task == 'collection':
            print("正在啟動怪物收藏模組...")
            collector = MonsterCollection(controller=xiao)
            collector.collect_and_start_monster_collection() # 假設主要執行方法是 start_collection
        elif task == 'daily':
            print("正在啟動每日準備模組...")
            preparer = DailyPrepare(controller=xiao)
            preparer.start_daily() # 假設主要執行方法是 run
        else:
            print(f"未知的任務：{task}")

if __name__ == "__main__":
    run()
