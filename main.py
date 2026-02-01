import sys
import os
import qdarkstyle
from PySide6.QtWidgets import QApplication
from src.utils.xiao_controller import XiaoController
from src.utils.settings_manager import SettingsManager
from src.ui.app_window import MainWindow
from src.ui.hardware_setup_dialog import HardwareSetupDialog


def main():
    """
    GUI 應用程式入口
    """
    # 隱藏 Windows 下常見的 Qt DPI 警告 (存取被拒)
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"
    app = QApplication(sys.argv)
    app.setOrganizationName("MapleScriptTeam")
    app.setApplicationName("MapleScript")

    # 套用深色主題並疊加自定義樣式 (加大 Checkbox)
    dark_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyside6')
    custom_stylesheet = """
        QCheckBox { spacing: 8px; font-size: 14px; }
        QCheckBox::indicator { width: 22px; height: 22px; }
    """
    app.setStyleSheet(dark_stylesheet + custom_stylesheet)

    settings_manager = SettingsManager()

    # --- Bootstrap 啟動迴圈 ---
    while True:
        # 嘗試建立連線並啟動主視窗
        try:
            # XiaoController 現在會自己去 SettingsManager 拿序號並找 Port
            with XiaoController() as xiao:
                print("硬體控制器連線成功")
                
                window = MainWindow(controller=xiao)
                window.show()
                
                # 開始事件迴圈，直到視窗關閉
                exit_code = app.exec()
                sys.exit(exit_code)
                
        except (Exception, SystemExit) as e:
            # 如果是 SystemExit (sys.exit 拋出的)，代表是正常關閉程式
            if isinstance(e, SystemExit):
                break
                
            # 否則就是連線失敗（找不到序號、或序號對應不到 Port）
            print(f"硬體連線失敗: {e}")
            
            # 彈出硬體設定視窗讓使用者選擇
            setup_dialog = HardwareSetupDialog(settings_manager)
            if setup_dialog.exec() == HardwareSetupDialog.Rejected:
                # 使用者取消設定，直接退出程式
                break
            
            # 如果使用者點擊確定並儲存了新序號，迴圈會繼續並嘗試重新連線

if __name__ == "__main__":
    main()
