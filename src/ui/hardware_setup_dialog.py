from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QMessageBox, QDialogButtonBox)
from src.utils.xiao_controller import XiaoController

class HardwareSetupDialog(QDialog):
    """
    硬體設定視窗：讓使用者選擇開發板。
    """
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("硬體連線設定")
        self.setMinimumWidth(400)
        
        self._init_ui()
        self.refresh_ports()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 1. 說明文字
        label = QLabel("請選擇您的開發板：")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        # 2. 下拉選單與重新整理按鈕
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setMinimumHeight(30)
        port_layout.addWidget(self.port_combo, stretch=4)

        btn_refresh = QPushButton("重新整理")
        btn_refresh.clicked.connect(self.refresh_ports)
        port_layout.addWidget(btn_refresh, stretch=1)
        
        layout.addLayout(port_layout)

        # 3. 提示資訊
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #aaa; margin-top: 10px;")
        layout.addWidget(self.info_label)

        # 4. 對話框按鈕 (確定 / 取消)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.handle_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def refresh_ports(self):
        """掃描系統中的 Ports 並更新選單"""
        self.port_combo.clear()
        ports = XiaoController.list_available_ports()
        
        if not ports:
            self.info_label.setText("⚠️ 找不到任何序列埠，請確認硬體已插好。")
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            return

        current_saved_serial = self.settings_manager.get("hardware", "serial_number")
        found_saved_index = -1

        for i, p in enumerate(ports):
            display_text = f"{p['port']} - {p['vendor']} （{p['description']}）"
            # 將序號儲存在 Data 角色中
            self.port_combo.addItem(display_text, p['serial_number'])
            
            # 如果目前顯示的正是之前儲存的序號，則紀錄其索引
            if p['serial_number'] and p['serial_number'] == current_saved_serial:
                found_saved_index = i

        if found_saved_index >= 0:
            self.port_combo.setCurrentIndex(found_saved_index)

        self.info_label.setText("提示：請選擇您的開發板所連接的連接埠。")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)

    def handle_accept(self):
        """按下確定後的處理邏輯"""
        selected_serial = self.port_combo.currentData()
        if not selected_serial:
            QMessageBox.warning(self, "警告", "所選裝置沒有序號，或未選擇有效裝置。")
            return
        
        # 儲存序號
        self.settings_manager.save("hardware", {"serial_number": selected_serial})
        self.accept()


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
