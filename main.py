import sys
import os
import qdarkstyle
from PySide6.QtWidgets import QApplication, QMessageBox
from src.utils.xiao_controller import XiaoController
from src.utils.settings_manager import SettingsManager
from src.ui.app_window import MainWindow
from src.ui.hardware_setup_dialog import HardwareSetupDialog

class ControllerMocker:

    pass


def show_no_hardware_warning():
    """
    彈出警告視窗，告知用戶未偵測到硬體。
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("硬體連線提示")
    msg.setText("由於目前未設置硬體輸入，因此將無法操控遊戲角色，請參考README設置CircuitPython設備")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


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
            
            # 顯示警告彈窗
            show_no_hardware_warning()
            
            # 彈出硬體設定視窗讓使用者選擇
            mocker = ControllerMocker()
            window = MainWindow(controller=mocker)
            window.show()

            # 開始事件迴圈，直到視窗關閉
            exit_code = app.exec()
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
