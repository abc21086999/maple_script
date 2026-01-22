import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QComboBox, QPushButton, QLabel, QScrollArea,
    QWidget, QFileDialog, QFrame, QDialogButtonBox, QMessageBox,
    QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class SkillRow(QWidget):
    def __init__(self, parent_dialog, data=None):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.image_path = None # 絕對路徑或相對路徑
        self._init_ui()
        if data:
            self._load_data(data)

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # 1. 啟用開關
        self.checkbox = QCheckBox()
        self.checkbox.setToolTip("啟用此技能")
        layout.addWidget(self.checkbox)

        # 2. 按鍵選擇
        self.key_combo = QComboBox()
        self.key_combo.setMinimumWidth(80)
        keys = (
            [chr(i) for i in range(ord('a'), ord('z')+1)] + 
            [str(i) for i in range(10)] + 
            ["'", '-', '=', '`', ';', '[', ']', ',', '.', '/', '\\'] +
            [f'f{i}' for i in range(1, 13)] +
            ['shift', 'ctrl', 'alt', 'space', 'insert', 'delete', 'home', 'end', 'pageup', 'pagedown']
        )
        self.key_combo.addItems(keys)
        layout.addWidget(self.key_combo)

        # 3. 圖片預覽區域
        self.image_label = QLabel()
        self.image_label.setFixedSize(40, 40)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #333;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # 4. 選擇圖片按鈕
        self.btn_load = QPushButton("📂")
        self.btn_load.setFixedSize(30, 30)
        self.btn_load.setToolTip("選擇技能圖片")
        self.btn_load.clicked.connect(self.select_image)
        layout.addWidget(self.btn_load)

        # 5. 刪除按鈕
        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.setStyleSheet("QPushButton { color: #ff6b6b; font-weight: bold; }")
        self.btn_delete.clicked.connect(self.delete_row)
        layout.addWidget(self.btn_delete)

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
        1. 檢查是否已經在 photos/skills 下
        2. 如果不在，複製過去
        3. 更新 UI 顯示與內部路徑紀錄
        """
        original_path = Path(original_path_str)
        project_root = Path(os.getcwd())
        target_dir = project_root / 'photos' / 'skills'
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
                        f'檔案 "{original_path.name}" 已存在於 photos/skills 資料夾中。\n是否要覆蓋它？',
                        QMessageBox.Yes | QMessageBox.No, 
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.No:
                        return # 使用者取消操作
                
                shutil.copy2(original_path, target_path)
            
            # 使用相對路徑更新 (photos/skills/xxx.png)
            relative_path = target_path.relative_to(project_root)
            self.set_image_path(str(relative_path))
            
        except Exception as e:
            print(f"Error copying image: {e}")
            # 如果複製失敗，就用原本的路徑，至少讓功能可用
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
        # 嘗試回傳相對路徑
        saved_path = ""
        if self.image_path:
            try:
                full_path = Path(self.image_path)
                saved_path = str(full_path.relative_to(os.getcwd()))
            except ValueError:
                saved_path = self.image_path
        
        # 統一使用 / 作為分隔符，避免 yaml 在不同 OS 出問題 (雖說這邊是 Windows)
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


class GrindSettingsDialog(QDialog):
    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.setWindowTitle("練功技能設定 (Grind Settings)")
        self.resize(550, 600)
        
        self.settings_manager = settings_manager
        self.rows = []
        
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 建立 Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Tab 1: 技能與按鍵 ---
        self.tab_skills = QWidget()
        self._setup_skills_tab()
        self.tabs.addTab(self.tab_skills, "技能與按鍵")

        # --- Tab 2: 保護設定 ---
        self.tab_protection = QWidget()
        self._setup_protection_tab()
        self.tabs.addTab(self.tab_protection, "保護設定")

        # Buttons (OK/Cancel)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _setup_skills_tab(self):
        layout = QVBoxLayout(self.tab_skills)

        header = QLabel("設定自動施放的技能與對應按鍵")
        header.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(header)
        
        sub_header = QLabel("圖片將自動儲存至 photos/skills 資料夾")
        sub_header.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(sub_header)

        # Scroll Area for Skills
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

        # Add Button
        btn_add = QPushButton("➕ 新增技能")
        btn_add.clicked.connect(self.add_row)
        layout.addWidget(btn_add)

    def _setup_protection_tab(self):
        layout = QVBoxLayout(self.tab_protection)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        header = QLabel("安全與暫停設定")
        header.setStyleSheet("font-weight: bold; margin-bottom: 10px; font-size: 14px;")
        layout.addWidget(header)

        # Checkbox 1: Stop when Rune appears
        self.chk_stop_rune = QCheckBox("當地圖上有輪時停止動作 (暫停)")
        self.chk_stop_rune.setToolTip("偵測到輪時，腳本將會暫停操作，直到輪消失")
        layout.addWidget(self.chk_stop_rune)

        # Checkbox 2: Stop when Other Players appear
        self.chk_stop_people = QCheckBox("當地圖上有其他人時停止動作 (暫停)")
        self.chk_stop_people.setToolTip("偵測到紅點(其他玩家)時，腳本將會暫停操作")
        layout.addWidget(self.chk_stop_people)

    def _load_settings(self):
        # 1. Load Skills
        skills_data = self.settings_manager.get("grind_skills", default=[])
        if not isinstance(skills_data, list):
            skills_data = []

        for item in skills_data:
            self.add_row(item)

        # 2. Load Protection Settings
        protection_data = self.settings_manager.get("grind_settings", default={})
        self.chk_stop_rune.setChecked(protection_data.get("stop_when_rune_appears", False))
        self.chk_stop_people.setChecked(protection_data.get("stop_when_people_appears", False))

    def add_row(self, data=None):
        if data is None:
            data = {'enabled': True, 'key': 'a', 'image_path': ''}
        
        row = SkillRow(self, data)
        self.scroll_layout.addWidget(row)
        self.rows.append(row)

    def remove_row(self, row_obj):
        if row_obj in self.rows:
            self.rows.remove(row_obj)

    def save_settings(self):
        # 1. Save Skills
        new_skills_data = []
        for row in self.rows:
            data = row.get_data()
            if not data['image_path']:
                continue
            new_skills_data.append(data)
            
        self.settings_manager.save("grind_skills", new_skills_data)

        # 2. Save Protection Settings
        protection_data = {
            "stop_when_rune_appears": self.chk_stop_rune.isChecked(),
            "stop_when_people_appears": self.chk_stop_people.isChecked()
        }
        self.settings_manager.save("grind_settings", protection_data)

        self.accept()
