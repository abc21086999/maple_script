import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, 
                               QDialogButtonBox, QLabel, QScrollArea, QWidget, QTabWidget,
                               QHBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class SkillRow(QWidget):
    def __init__(self, parent_dialog, base_data_path, data=None):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.base_data_path = base_data_path
        self.image_path = None # 絕對路徑或相對路徑
        self._init_ui()
        if data:
            self._load_data(data)

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # 1. 啟用開關
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(30)
        self.checkbox.setToolTip("啟用此技能")
        layout.addWidget(self.checkbox)
        
        layout.addStretch(1)

        # 2. 按鍵選擇
        self.key_combo = QComboBox()
        self.key_combo.setMinimumWidth(120)
        keys = (
            [chr(i) for i in range(ord('a'), ord('z')+1)] + 
            [str(i) for i in range(10)] + 
            ["'", '-', '=', '`', ';', '[', ']', ',', '.', '/', '\\'] +
            [f'f{i}' for i in range(1, 13)] +
            ['shift', 'ctrl', 'alt', 'space', 'insert', 'delete', 'home', 'end', 'pageup', 'pagedown']
        )
        self.key_combo.addItems(keys)
        layout.addWidget(self.key_combo)
        
        layout.addStretch(1)

        # 3. 圖片預覽區域
        self.image_label = QLabel()
        self.image_label.setFixedSize(40, 40)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #333;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)
        
        layout.addStretch(1)

        # 4. 選擇圖片按鈕
        self.btn_load = QPushButton("📂")
        self.btn_load.setFixedSize(30, 30)
        self.btn_load.setToolTip("選擇技能圖片")
        self.btn_load.clicked.connect(self.select_image)
        layout.addWidget(self.btn_load)
        
        layout.addStretch(1)

        # 5. 刪除按鈕
        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.setStyleSheet("QPushButton { color: #ff6b6b; font-weight: bold; }")
        self.btn_delete.clicked.connect(self.delete_row)
        layout.addWidget(self.btn_delete)

        layout.addStretch(1)

    def _load_data(self, data):
        self.checkbox.setChecked(data.get('enabled', True))
        
        key = data.get('key', 'a')
        index = self.key_combo.findText(key, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.key_combo.setCurrentIndex(index)
            
        path_str = data.get('image_path', '')
        if path_str:
            self.set_image_path(path_str)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "選擇技能截圖", 
            os.getcwd(), 
            "Images (*.png *.jpg *.bmp)"
        )
        if file_name:
            self.process_selected_image(file_name)

    def process_selected_image(self, original_path_str):
        """
        處理使用者選擇的圖片：
        1. 將圖片複製到 AppData/toggle 下
        2. 更新 UI 顯示與內部路徑紀錄
        """
        original_path = Path(original_path_str)
        # 目標資料夾：AppData/toggle
        target_dir = self.base_data_path / 'toggle'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 目標檔案路徑 (保留原檔名)
        target_path = target_dir / original_path.name
        
        try:
            # 如果來源不是目標路徑 (避免自己複製自己)
            if original_path.resolve() != target_path.resolve():
                # 如果目標檔案已存在，詢問是否覆蓋
                if target_path.exists():
                    reply = QMessageBox.question(
                        self, 
                        '覆蓋確認', 
                        f'檔案 "{original_path.name}" 已存在於 AppData/toggle 資料夾中。\n是否要覆蓋它？',
                        QMessageBox.Yes | QMessageBox.No, 
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.No:
                        return # 使用者取消操作
                
                shutil.copy2(original_path, target_path)
            
            # 使用絕對路徑更新
            self.set_image_path(str(target_path))
            
        except Exception as e:
            print(f"Error copying image: {e}")
            self.set_image_path(original_path_str)

    def set_image_path(self, path_str):
        path = Path(path_str)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
            
        if path.exists():
            self.image_path = str(path) # 暫存絕對路徑用於顯示
            pixmap = QPixmap(str(path))
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.image_label.setText("遺失")
            self.image_path = path_str # 雖然遺失還是存著

    def get_data(self):
        # 直接使用儲存的路徑 (通常是 AppData 的絕對路徑)
        saved_path = self.image_path if self.image_path else ""
        
        # 統一使用 / 作為分隔符
        saved_path = saved_path.replace('\\', '/')

        return {
            'enabled': self.checkbox.isChecked(),
            'key': self.key_combo.currentText(),
            'image_path': saved_path
        }

    def delete_row(self):
        self.setParent(None)
        self.deleteLater()
        self.parent_dialog.remove_row(self)

class SettingsDialog(QDialog):
    """
    通用的設定視窗，用於開關各個子任務。
    """
    # 集中管理所有腳本的顯示名稱，按 Section 分類
    SECTION_DISPLAY_NAMES = {
        'daily_prepare': {
            'switch_set': '切換練功套組 (Switch Set)',
            'union_coin': '領取戰地硬幣 (Union Coin)',
            'toggle_skills': '開關技能 (Toggle Skills)',
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
        self.rows = []

        # 1. 讀取目前的設定
        self.current_settings = self.settings_manager.get(self.section_key)
        
        # 2. 建立 UI
        self._setup_ui()
        
        # 3. 讀取 Toggle Skills 設定 (如果在這個 section 有支援的話)
        if self.section_key == 'daily_prepare':
            self._load_toggle_skills()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 建立分頁元件
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- 第一頁：一般設定 (原本的勾選清單) ---
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # 說明文字
        tab1_layout.addWidget(QLabel("請勾選欲執行的子任務："))

        # 捲動區域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(content_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 排序邏輯：優先使用 self.display_names 裡定義的順序，並包含 current_settings 裡所有的 key
        all_keys = list(self.display_names.keys())
        for k in self.current_settings.keys():
            if k not in all_keys:
                all_keys.append(k)
        
        def sort_key(k):
            display_keys = list(self.display_names.keys())
            if k in display_keys:
                return display_keys.index(k)
            return 999

        sorted_keys = sorted(all_keys, key=sort_key)

        # 動態產生 Checkbox
        for key in sorted_keys:
            # 取得目前的設定值，若不存在則預設為 False
            value = self.current_settings.get(key, False)
            # 優先從當前 section 的名稱表找，找不到就直接顯示原始 key
            display_text = self.display_names.get(key, key)
            
            cb = QCheckBox(display_text)
            cb.setChecked(bool(value))
            self.scroll_layout.addWidget(cb)
            self.checkboxes[key] = cb

        scroll.setWidget(content_widget)
        tab1_layout.addWidget(scroll)
        
        self.tabs.addTab(tab1, "一般設定")

        # --- 第二頁：開關技能 (僅在 daily_prepare 顯示) ---
        if self.section_key == 'daily_prepare':
            tab2 = QWidget()
            tab2_layout = QVBoxLayout(tab2)
            
            header = QLabel("設定自動施放的開關技能 (Toggle Skills)")
            header.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            tab2_layout.addWidget(header)
            
            sub_header = QLabel("圖片將自動儲存至系統 AppData 資料夾")
            sub_header.setStyleSheet("color: gray; margin-bottom: 10px;")
            tab2_layout.addWidget(sub_header)

            # Scroll Area for Skills
            skill_scroll = QScrollArea()
            skill_scroll.setWidgetResizable(True)
            self.skill_scroll_content = QWidget()
            self.skill_scroll_layout = QVBoxLayout(self.skill_scroll_content)
            self.skill_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            skill_scroll.setWidget(self.skill_scroll_content)
            tab2_layout.addWidget(skill_scroll)

            # Add Button
            btn_add = QPushButton("➕ 新增技能")
            btn_add.clicked.connect(self.add_row)
            tab2_layout.addWidget(btn_add)
            
            self.tabs.addTab(tab2, "開關技能")

        # 按鈕區 (確定/取消) - 放在分頁外面，共用
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def add_row(self, data=None):
        if data is None:
            data = {'enabled': True, 'key': 'a', 'image_path': ''}
        
        row = SkillRow(self, self.settings_manager.base_data_path, data)
        self.skill_scroll_layout.addWidget(row)
        self.rows.append(row)

    def remove_row(self, row_obj):
        if row_obj in self.rows:
            self.rows.remove(row_obj)

    def _load_toggle_skills(self):
        """讀取開關技能設定"""
        skills_data = self.settings_manager.get("toggle_skills", default=[])
        if not isinstance(skills_data, list):
            skills_data = []

        for item in skills_data:
            self.add_row(item)

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
        # 1. 儲存一般設定
        new_data = self.get_new_settings()
        self.settings_manager.save(self.section_key, new_data)

        # 2. 儲存開關技能 (如果有的話)
        if self.section_key == 'daily_prepare':
            new_skills_data = []
            for row in self.rows:
                data = row.get_data()
                if not data['image_path']:
                    continue
                new_skills_data.append(data)
            self.settings_manager.save("toggle_skills", new_skills_data)

    def accept(self):
        self.save_settings()
        super().accept()