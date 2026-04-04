import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QComboBox, QPushButton, QLabel, QScrollArea,
    QWidget, QFileDialog, QFrame, QDialogButtonBox, QMessageBox,
    QTabWidget, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from src.RouteRecorder import RouteRecorder
import ctypes
import sys
import subprocess

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
        
        # 套用方法 B：在所有元件之間與兩端都加入彈簧
        # layout.addStretch(1)

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
        1. 將圖片複製到 AppData/skills 下
        2. 更新 UI 顯示與內部路徑紀錄
        """
        original_path = Path(original_path_str)
        # 目標資料夾：AppData/skills
        target_dir = self.base_data_path / 'skills'
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
                        f'檔案 "{original_path.name}" 已存在於 AppData/skills 資料夾中。\n是否要覆蓋它？',
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


class GrindSettingsDialog(QDialog):
    def __init__(self, parent, settings_manager, task_manager=None, controller=None):
        super().__init__(parent)
        self.setWindowTitle("練功技能設定 (Grind Settings)")
        self.resize(450, 650)
        
        self.settings_manager = settings_manager
        self.task_manager = task_manager
        self.controller = controller
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

        # --- Tab 2: 路徑錄製 ---
        if self.task_manager and self.controller:
            self.tab_recorder = QWidget()
            self._setup_recorder_tab()
            self.tabs.addTab(self.tab_recorder, "路徑錄製")

        # --- Tab 3: 保護設定 ---
        self.tab_protection = QWidget()
        self._setup_protection_tab()
        self.tabs.addTab(self.tab_protection, "保護設定")

        # Buttons (OK/Cancel)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _setup_recorder_tab(self):
        layout = QVBoxLayout(self.tab_recorder)
        
        # --- 1. 執行設定 (原本在下面，現在移到上面) ---
        setting_header = QLabel("腳本執行設定")
        setting_header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(setting_header)

        # Checkbox 1: 啟用錄製的腳本
        self.chk_enable_route = QCheckBox("啟用錄製的腳本")
        self.chk_enable_route.setToolTip("勾選後，將會在練功時自動執行錄製的路徑")
        self.chk_enable_route.toggled.connect(self.update_loop_ui_state)
        layout.addWidget(self.chk_enable_route)

        # 循環間隔設定 (Horizontal Layout)
        loop_layout = QHBoxLayout()
        loop_layout.setContentsMargins(20, 0, 0, 0) # 縮排

        # Checkbox 2: 啟用間隔
        self.chk_enable_interval = QCheckBox("啟用循環冷卻：每")
        self.chk_enable_interval.toggled.connect(self.update_loop_ui_state)
        loop_layout.addWidget(self.chk_enable_interval)

        # ComboBox: 秒數選擇
        self.combo_loop_interval = QComboBox()
        # 產生 5, 10, ..., 60 的選項
        intervals = [str(i) for i in range(5, 360, 5)]
        self.combo_loop_interval.addItems(intervals)
        self.combo_loop_interval.setFixedWidth(60)
        loop_layout.addWidget(self.combo_loop_interval)

        # Label: 單位
        loop_layout.addWidget(QLabel("秒重複一次"))
        loop_layout.addStretch() # 靠左對齊
        layout.addLayout(loop_layout)

        # 分隔線
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("margin: 10px 0;")
        layout.addWidget(line)

        # --- 2. 錄製控制項 (原本在上面，現在移到下面) ---
        header = QLabel("錄製新路徑")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # 說明
        desc = QLabel(
            "功能說明：\n"
            "1. 點擊「開始錄製」後，程式會切換至遊戲視窗。\n"
            "2. 請輸入您的練功迴圈 (移動、跳躍、技能)。\n"
            "3. 完成後，用滑鼠切換回此視窗並點擊「停止錄製」。\n"
            "4. 錄製需要系統管理員權限，請確保程式已以管理員權限啟動"
        )
        desc.setStyleSheet("color: gray; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 控制按鈕區
        btn_layout = QHBoxLayout()
        
        self.btn_start_record = QPushButton("🔴 開始錄製")
        self.btn_start_record.setMinimumHeight(40)
        self.btn_start_record.clicked.connect(self.start_recording)
        btn_layout.addWidget(self.btn_start_record)

        self.btn_stop_record = QPushButton("⏹ 停止錄製")
        self.btn_stop_record.setMinimumHeight(40)
        self.btn_stop_record.clicked.connect(self.stop_recording)
        self.btn_stop_record.setEnabled(False) # 初始為停用
        btn_layout.addWidget(self.btn_stop_record)
        layout.addLayout(btn_layout)

        # 狀態顯示
        self.lbl_status = QLabel("狀態: 閒置中")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("font-weight: bold; margin: 10px; color: #4facfe;")
        layout.addWidget(self.lbl_status)

        layout.addStretch() # 將內容推到頂部

    def update_loop_ui_state(self):
        """根據 Checkbox 狀態啟用/停用 UI"""
        route_enabled = self.chk_enable_route.isChecked()
        self.chk_enable_interval.setEnabled(route_enabled)
        
        interval_enabled = self.chk_enable_interval.isChecked()
        self.combo_loop_interval.setEnabled(route_enabled and interval_enabled)

    def start_recording(self):
        # 檢查管理員權限 (錄製鍵盤需要)
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False

        if not is_admin:
            QMessageBox.warning(
                self,
                "權限不足",
                "由於錄製鍵盤輸入需要系統管理員權限，請將程式以系統管理員權限開啟",
                QMessageBox.Ok
            )
            return

        if not self.task_manager or not self.controller:
            return

        self.btn_start_record.setEnabled(False)
        self.btn_stop_record.setEnabled(True)
        self.lbl_status.setText("狀態: 正在錄製中...")
        self.lbl_status.setStyleSheet("font-weight: bold; margin: 10px; color: #ff6b6b;")

        # 啟動錄製任務
        self.task_manager.start_task(
            RouteRecorder, 
            self.controller
        )

    def stop_recording(self):
        if self.task_manager:
            self.task_manager.stop_task()
            self.lbl_status.setText("狀態: 正在停止...")
            self.reset_recorder_ui()

    def reset_recorder_ui(self):
        self.btn_start_record.setEnabled(True)
        self.btn_stop_record.setEnabled(False)
        self.lbl_status.setText("狀態: 錄製完成")
        self.lbl_status.setStyleSheet("font-weight: bold; margin: 10px; color: #4facfe;")

    def update_stationary_ui_state(self):
        """根據定點練功 Checkbox 狀態啟用/停用『按下上』"""
        stationary_enabled = self.chk_stationary.isChecked()
        self.chk_random_up.setEnabled(stationary_enabled)

    def _setup_skills_tab(self):
        layout = QVBoxLayout(self.tab_skills)

        header = QLabel("設定自動施放的技能與對應按鍵")
        header.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(header)
        
        # 啟用定點練功
        self.chk_stationary = QCheckBox("啟用定點練功")
        self.chk_stationary.toggled.connect(self.update_stationary_ui_state)
        layout.addWidget(self.chk_stationary)
        
        # 不定時按下『上』來透過地圖上的傳點移動
        hbox_up = QHBoxLayout()
        hbox_up.setContentsMargins(20, 0, 0, 0)
        self.chk_random_up = QCheckBox("不定時按下『上』來透過地圖上的傳點移動")
        hbox_up.addWidget(self.chk_random_up)
        layout.addLayout(hbox_up)

        sub_header = QLabel("圖片將自動儲存至系統 AppData 資料夾")
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

        # Checkbox 3: Auto solve Rune (Experimental)
        self.chk_auto_solve_rune = QCheckBox("自動解除地圖輪迴（實驗）")
        self.chk_auto_solve_rune.setToolTip("勾選後，腳本將會自動嘗試解除地圖上的符文")
        self.chk_auto_solve_rune.toggled.connect(self.update_rune_ui_state)
        layout.addWidget(self.chk_auto_solve_rune)

        # 常用攻擊技能按鍵 (Horizontal Layout with indentation)
        rune_layout = QHBoxLayout()
        rune_layout.setContentsMargins(30, 0, 0, 0)
        
        self.lbl_normal_skill = QLabel("您的常用攻擊技能按鍵")
        rune_layout.addWidget(self.lbl_normal_skill)

        self.combo_normal_skill = QComboBox()
        self.combo_normal_skill.setMinimumWidth(120)
        keys = (
            [chr(i) for i in range(ord('a'), ord('z')+1)] + 
            [str(i) for i in range(10)] + 
            ["'", '-', '=', '`', ';', '[', ']', ',', '.', '/', '\\'] +
            [f'f{i}' for i in range(1, 13)] +
            ['shift', 'ctrl', 'alt', 'space', 'insert', 'delete', 'home', 'end', 'pageup', 'pagedown']
        )
        self.combo_normal_skill.addItems(keys)
        rune_layout.addWidget(self.combo_normal_skill)
        rune_layout.addStretch()
        layout.addLayout(rune_layout)

    def update_rune_ui_state(self):
        """根據 Checkbox 狀態啟用/停用『解除符文』按鍵選單"""
        rune_enabled = self.chk_auto_solve_rune.isChecked()
        self.lbl_normal_skill.setEnabled(rune_enabled)
        self.combo_normal_skill.setEnabled(rune_enabled)

    def _load_settings(self):
        # 1. Load Skills
        skills_data = self.settings_manager.get("grind_skills", default=[])
        if not isinstance(skills_data, list):
            skills_data = []

        for item in skills_data:
            self.add_row(item)

        # 2. Load Protection Settings & Loop Settings
        protection_data = self.settings_manager.get("grind_settings", default={})
        self.chk_stop_rune.setChecked(protection_data.get("stop_when_rune_appears", False))
        self.chk_stop_people.setChecked(protection_data.get("stop_when_people_appears", False))
        self.chk_auto_solve_rune.setChecked(protection_data.get("auto_solve_rune", False))
        self.chk_stationary.setChecked(protection_data.get("stationary_mode", False))
        self.chk_random_up.setChecked(protection_data.get("random_up_movement", False))

        self.update_stationary_ui_state()
        self.update_rune_ui_state()

        # Load Normal Skill Key
        normal_skill_data = self.settings_manager.get("normal_skills", default={})
        normal_key = normal_skill_data.get("normal", "a")
        index = self.combo_normal_skill.findText(normal_key)
        if index >= 0:
            self.combo_normal_skill.setCurrentIndex(index)
        
        # Loop Settings
        if hasattr(self, 'chk_enable_route'): # 確保元件已建立
            self.chk_enable_route.setChecked(protection_data.get("enable_loop_route", False))
            self.chk_enable_interval.setChecked(protection_data.get("enable_loop_interval", False))
            
            interval = str(protection_data.get("loop_route_interval", 5))
            index = self.combo_loop_interval.findText(interval)
            if index >= 0:
                self.combo_loop_interval.setCurrentIndex(index)
            
            self.update_loop_ui_state()

    def add_row(self, data=None):
        if data is None:
            data = {'enabled': True, 'key': 'a', 'image_path': ''}
        
        row = SkillRow(self, self.settings_manager.base_data_path, data)
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

        # 2. Save Protection & Loop Settings
        protection_data = {
            "stop_when_rune_appears": self.chk_stop_rune.isChecked(),
            "stop_when_people_appears": self.chk_stop_people.isChecked(),
            "auto_solve_rune": self.chk_auto_solve_rune.isChecked(),
            "stationary_mode": self.chk_stationary.isChecked(),
            "random_up_movement": self.chk_random_up.isChecked(),
            # Loop Settings
            "enable_loop_route": self.chk_enable_route.isChecked() if hasattr(self, 'chk_enable_route') else False,
            "enable_loop_interval": self.chk_enable_interval.isChecked() if hasattr(self, 'chk_enable_interval') else False,
            "loop_route_interval": int(self.combo_loop_interval.currentText()) if hasattr(self, 'combo_loop_interval') else 5
        }
        self.settings_manager.save("grind_settings", protection_data)

        # 3. Save Normal Skill Key
        normal_skill_data = {
            "normal": self.combo_normal_skill.currentText()
        }
        self.settings_manager.save("normal_skills", normal_skill_data)

    def accept(self):
        self.save_settings()
        super().accept()
