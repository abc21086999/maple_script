from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QDialogButtonBox, QMessageBox)
from src.utils.secret_manager import SecretManager

class StorageSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定倉庫密碼")
        self.resize(300, 150)
        self._setup_ui()
        self._load_current_password()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 說明標籤
        label = QLabel("請輸入第二組密碼 (倉庫密碼)：")
        layout.addWidget(label)

        # 密碼輸入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("在此輸入密碼")
        layout.addWidget(self.password_input)

        # 按鈕區 (儲存/取消)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_current_password(self):
        """嘗試讀取現有密碼並預填 (方便修改)"""
        current_pw = SecretManager.get_storage_password()
        if current_pw:
            self.password_input.setText(current_pw)

    def save_password(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "警告", "密碼不能為空")
            return
        
        try:
            SecretManager.set_storage_password(password)
            QMessageBox.information(self, "成功", "密碼已儲存")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存密碼時發生錯誤：\n{str(e)}")
