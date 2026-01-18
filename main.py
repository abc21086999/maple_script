import sys
from dotenv import load_dotenv
from src.utils.xiao_controller import XiaoController
from PySide6.QtWidgets import QApplication
from src.ui.app_window import MainWindow

# 確保可以導入 src 下的模組
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    GUI 應用程式入口
    """
    load_dotenv()

    # 建立 QApplication
    app = QApplication(sys.argv)
    
    # 套用主題
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    except ImportError:
        pass

    # 初始化硬體控制器
    # 使用 with 上下文管理器確保資源自動釋放
    try:
        with XiaoController() as xiao:
            print("硬體控制器已連接")
            
            window = MainWindow(controller=xiao)
            window.show()
            
            # 開始事件迴圈，程式會在這裡暫停直到視窗關閉
            sys.exit(app.exec())
            
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        # 如果是 SystemExit (sys.exit 拋出的)，通常是正常退出，不需要暫停
        if not isinstance(e, SystemExit):
            input("輸入任意鍵繼續...")

if __name__ == "__main__":
    main()
