import sys
from dotenv import load_dotenv
from src.utils.xiao_controller import XiaoController
from PySide6.QtWidgets import QApplication
from src.ui.app_window import MainWindow
import os
import qdarkstyle


def main():
    """
    GUI 應用程式入口
    """
    # 隱藏 Windows 下常見的 Qt DPI 警告 (存取被拒)
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"
    
    load_dotenv()
    app = QApplication(sys.argv)
    app.setOrganizationName("MapleScriptTeam")
    app.setApplicationName("MapleScript")

    # 套用深色主題並疊加自定義樣式 (加大 Checkbox)
    dark_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyside6')
    custom_stylesheet = """
        QCheckBox {
            spacing: 8px;
            font-size: 14px;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
        }
    """
    app.setStyleSheet(dark_stylesheet + custom_stylesheet)

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
