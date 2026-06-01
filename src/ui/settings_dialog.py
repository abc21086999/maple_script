import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, 
                               QDialogButtonBox, QLabel, QScrollArea, QWidget, QTabWidget,
                               QHBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

HD_REWARD_OPTIONS = {
    'take_core': '核心寶石',
    'take_arcane': '密法符文交換券',
    'take_authentic': '真實符文交換券',
    'pendant_of_spirit': '精靈墜飾',
    'exp_3x_coupon': '經驗值3倍券',
    'slot_expansion': '欄位擴充選擇券',
    'milestone_25': '25里程',
    'medal_of_honor': '特殊名譽勳章',
    'royal_face': '皇家整形交換券',
    'royal_hair': '皇家美髮交換券',
    'coloring_coupon': '染色券',
    'typhoon_growth': '颱風成長祕藥',
    'beauty_album_slot': '美容相簿欄位擴充券',
    'karma_rare_scroll': '卡勒馬附加稀有捲軸',
    'grand_gift': '特級禮物 (最後一天)',
}
# TODO: 真實符文交換券, 美容相簿欄位擴充券, 卡勒馬附加稀有捲軸, 特級禮物

class SkillRow(QWidget):
    def __init__(self, parent_dialog, base_data_path, data=None, subfolder='toggle', show_key=True):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.base_data_path = base_data_path
        self.subfolder = subfolder
        self.show_key = show_key
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
        self.checkbox.setToolTip("啟用此項目")
        layout.addWidget(self.checkbox)
        
        layout.addStretch(1)

        # 2. 按鍵選擇 (選用)
        if self.show_key:
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
        else:
            self.key_combo = None

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
        self.btn_load.setToolTip("選擇圖片")
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
        
        if self.key_combo:
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
        1. 將圖片複製到 AppData/{subfolder} 下
        2. 更新 UI 顯示與內部路徑紀錄
        """
        original_path = Path(original_path_str)
        # 目標資料夾：AppData/{subfolder}
        target_dir = self.base_data_path / self.subfolder
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
                        f'檔案 "{original_path.name}" 已存在於 AppData/{self.subfolder} 資料夾中。\n是否要覆蓋它？',
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
            'key': self.key_combo.currentText() if self.key_combo else 'a',
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
        self.hd_reward_checkboxes = {}
        self.toggle_skill_rows = []
        self.grind_set_rows = []
        self.toggle_skill_layout = None
        self.grind_set_layout = None

        # 1. 讀取目前的設定
        self.current_settings = self.settings_manager.get(self.section_key)
        
        # 2. 建立 UI
        self._setup_ui()
        
        # 3. 讀取自訂分頁資料 (如果在這個 section 有支援的話)
        if self.section_key == 'daily_prepare':
            self._load_custom_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 建立分頁元件
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- 第一頁：一般設定 (原本的勾選清單) ---
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # 說明文字
        tab1_header = QLabel("請勾選欲執行的子任務：")
        tab1_header.setStyleSheet("font-weight: bold; margin-bottom: 5px; font-size: 14px;")
        tab1_layout.addWidget(tab1_header)

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

        # --- 其他分頁 (僅在 daily_prepare 顯示) ---
        if self.section_key == 'daily_prepare':
            # 第二頁：開關技能
            self.toggle_skill_layout = self._setup_skill_like_tab(
                "開關技能", 
                "設定自動施放的開關技能 (Toggle Skills)",
                "請放入遊戲右上角開關技能的截圖，及對應按鍵",
                "toggle_skills",
                self.toggle_skill_rows,
                "toggle",
                "➕ 新增圖片",
                show_key=True
            )
            
            # 第三頁：練功套組
            self.grind_set_layout = self._setup_skill_like_tab(
                "練功套組",
                "設定角色練功套組的圖示",
                "請放入角色套組介面中，練功套組的圖示截圖",
                "grind_set",
                self.grind_set_rows,
                "grind_set",
                "➕ 新增圖片",
                show_key=False
            )
            
            # 第四頁：HD 獎勵設定
            self._setup_hd_tab()

        # 按鈕區 (確定/取消) - 放在分頁外面，共用
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _setup_skill_like_tab(self, tab_title, header_text, sub_header_text, settings_key, rows_list, subfolder, add_button_text, show_key=True):
        """通用方法建立類似技能列表的分頁"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        header = QLabel(header_text)
        header.setStyleSheet("font-weight: bold; margin-bottom: 5px; font-size: 14px;")
        tab_layout.addWidget(header)
        
        sub_header = QLabel(sub_header_text)
        sub_header.setStyleSheet("color: gray; margin-bottom: 10px; font-size: 14px;")
        tab_layout.addWidget(sub_header)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(scroll_content)
        tab_layout.addWidget(scroll)

        # Add Button
        btn_add = QPushButton(add_button_text)
        # 使用 lambda 傳遞參數給 add_row
        btn_add.clicked.connect(lambda: self.add_row(None, rows_list, scroll_layout, subfolder, show_key))
        tab_layout.addWidget(btn_add)
        
        self.tabs.addTab(tab, tab_title)
        return scroll_layout

    def _setup_hd_tab(self):
        """建立 HD 獎勵設定分頁"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        header = QLabel("HD 獎勵設定")
        header.setStyleSheet("font-weight: bold; margin-bottom: 5px; font-size: 14px;")
        tab_layout.addWidget(header)
        
        sub_header = QLabel("請勾選想要領取的 HD 獎勵項目 (將依序搜尋)：")
        sub_header.setStyleSheet("color: gray; margin-bottom: 10px; font-size: 14px;")
        tab_layout.addWidget(sub_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 依照 HD_REWARD_OPTIONS 建立 Checkbox
        for key, display_name in HD_REWARD_OPTIONS.items():
            cb = QCheckBox(display_name)
            layout.addWidget(cb)
            self.hd_reward_checkboxes[key] = cb

        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "HD設定")

    def add_row(self, data=None, rows_list=None, layout=None, subfolder='toggle', show_key=True):
        if rows_list is None:
            rows_list = self.toggle_skill_rows
        if layout is None:
            layout = self.toggle_skill_layout
            
        if data is None:
            data = {'enabled': True, 'key': 'a', 'image_path': ''}
        
        row = SkillRow(self, self.settings_manager.base_data_path, data, subfolder, show_key)
        layout.addWidget(row)
        rows_list.append(row)

    def remove_row(self, row_obj):
        if row_obj in self.toggle_skill_rows:
            self.toggle_skill_rows.remove(row_obj)
        elif row_obj in self.grind_set_rows:
            self.grind_set_rows.remove(row_obj)

    def _load_custom_data(self):
        """讀取自訂分頁設定 (開關技能、練功套組)"""
        # 1. 讀取開關技能
        skills_data = self.settings_manager.get("toggle_skills", default=[])
        if isinstance(skills_data, list):
            for item in skills_data:
                self.add_row(item, self.toggle_skill_rows, self.toggle_skill_layout, "toggle", show_key=True)

        # 2. 讀取練功套組
        grind_set_data = self.settings_manager.get("grind_set", default=[])
        if isinstance(grind_set_data, list):
            for item in grind_set_data:
                self.add_row(item, self.grind_set_rows, self.grind_set_layout, "grind_set", show_key=False)

        # 3. 讀取 HD 獎勵勾選設定
        hd_rewards = self.settings_manager.get("hd_rewards", default={})
        for key, cb in self.hd_reward_checkboxes.items():
            cb.setChecked(hd_rewards.get(key, False))

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

        # 2. 儲存自訂分頁資料
        if self.section_key == 'daily_prepare':
            # 儲存開關技能
            new_skills_data = []
            for row in self.toggle_skill_rows:
                data = row.get_data()
                if not data['image_path']:
                    continue
                new_skills_data.append(data)
            self.settings_manager.save("toggle_skills", new_skills_data)
            
            # 儲存練功套組
            new_grind_set_data = []
            for row in self.grind_set_rows:
                data = row.get_data()
                if not data['image_path']:
                    continue
                new_grind_set_data.append(data)
            self.settings_manager.save("grind_set", new_grind_set_data)
            
            # 儲存 HD 獎勵勾選設定
            new_hd_rewards = {}
            for key, cb in self.hd_reward_checkboxes.items():
                new_hd_rewards[key] = cb.isChecked()
            self.settings_manager.save("hd_rewards", new_hd_rewards)

    def accept(self):
        self.save_settings()
        super().accept()