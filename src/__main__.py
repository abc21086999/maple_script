import sys
from dotenv import load_dotenv
from src.MapleGrind import MapleGrind
from src.MonsterCollection import MonsterCollection
from src.DailyPrepare import DailyPrepare
from src.Storage import Storage
from src.utils.xiao_controller import XiaoController
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

GUAI_GUAI_BANNER = r"""
 _________________________________________________
|/////////////////////////////////////////////////|
|//_____________________________________________//|
|/                                               \|
| [ GUAI GUAI ]        STABILITY LEVEL: MAXIMUM   |
|                                                 |
|       _________________________________         |
|      |                                 |        |
|      |    綠  色  。  乖  。  乖       |        |
|      |_________________________________|        |
|                                                 |
|               ( 奶油椰子口味 )                  |
|                                                 |
|    _________________________________________    |
|   |                                         |   |
|   |            機   房   重   地            |   |
|   |                                         |   |
|   |         B U G   S T A Y   A W A Y       |   |
|   |_________________________________________|   |
|                                                 |
|    [ 專用電腦 ] [ 楓之谷腳本 ] [ 運作中... ]    |
|                                                 |
|_________________________________________________|
|\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\|
|_________________________________________________|
"""

def run():
    """
    應用程式主入口
    """
    print(GUAI_GUAI_BANNER)
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
