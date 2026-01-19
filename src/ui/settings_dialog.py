from PySide6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, 
                               QDialogButtonBox, QLabel, QScrollArea, QWidget)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """
    通用的設定視窗，用於開關各個子任務。
    """
    # 集中管理所有腳本的顯示名稱，按 Section 分類
    SECTION_DISPLAY_NAMES = {
        'daily_prepare': {
            'switch_set': '切換練功套組 (Switch Set)',
            'union_coin': '領取戰地硬幣 (Union Coin)',
            'daily_mission': '每日/每週任務 (Daily/Weekly)',
            'dismantle': '分解裝備 (Dismantle)',
            'hd_gift': '領取 HD 獎勵',
            'milestone': '領取里程 (Milestone)',
            'market': '處理拍賣場 (Market)',
            'master_apprentice': '師徒系統 (Master/Apprentice)',
            'event': '活動簽到 (Event)',
            'housing': '小屋對話 (Housing)',
        },
        'monster_collection': {
            # 暫時留空
        },
        'daily_boss': {
            # 暫時留空
        },
        'storage': {
            # 暫時留空
        }
    }

    def __init__(self, parent, settings_manager, section_key, title="任務設定"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 500)
        
        self.settings_manager = settings_manager
        self.section_key = section_key
        
        # 根據傳入的 section_key 取得對應的名稱表
        self.display_names = self.SECTION_DISPLAY_NAMES.get(self.section_key, {})
        self.checkboxes = {}

        # 1. 讀取目前的設定
        self.current_settings = self.settings_manager.get(self.section_key)
        
        # 2. 建立 UI
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 說明文字
        layout.addWidget(QLabel("請勾選欲執行的子任務："))

        # 捲動區域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(content_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 排序邏輯：優先使用 self.display_names 裡定義的順序
        keys_in_settings = list(self.current_settings.keys())
        
        def sort_key(k):
            display_keys = list(self.display_names.keys())
            if k in display_keys:
                return display_keys.index(k)
            return 999

        sorted_keys = sorted(keys_in_settings, key=sort_key)

        # 動態產生 Checkbox
        for key in sorted_keys:
            value = self.current_settings[key]
            # 優先從當前 section 的名稱表找，找不到就直接顯示原始 key
            display_text = self.display_names.get(key, key)
            
            cb = QCheckBox(display_text)
            cb.setChecked(bool(value))
            self.scroll_layout.addWidget(cb)
            self.checkboxes[key] = cb

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # 按鈕區 (確定/取消)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_new_settings(self):
        """
        取得使用者修改後的設定 (Dict)
        """
        new_settings = {}
        for key, cb in self.checkboxes.items():
            new_settings[key] = cb.isChecked()
        return new_settings

    def save_settings(self):
        """
        將目前的 UI 狀態寫回設定檔
        """
        new_data = self.get_new_settings()
        self.settings_manager.save(self.section_key, new_data)