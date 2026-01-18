from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTextEdit, QLabel, QFrame)
from PySide6.QtCore import Signal, QObject, Slot, Qt
from src.ui.task_manager import TaskManager
from src.MapleGrind import MapleGrind
from src.DailyPrepare import DailyPrepare
from src.MonsterCollection import MonsterCollection
from src.DailyBoss import DailyBoss
from src.Storage import Storage
from src.DancingMachine import Dancing

class LogSignal(QObject):
    """
    用於跨執行緒發送 Log 訊息的信號類別
    """
    text_written = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.setWindowTitle("Automation Control Center")
        self.resize(900, 600)
        
        # 建立中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局 (水平分割：左邊按鈕，右邊 Log)
        main_layout = QHBoxLayout(central_widget)
        
        # --- 左側控制面板 ---
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 標題
        title_label = QLabel("任務選擇")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        left_layout.addWidget(title_label)
        
        # 按鈕群 (使用 helper function 建立按鈕以保持程式碼整潔)
        self.add_task_button(left_layout, "開始練功 (Grind)", self.start_grind)
        self.add_task_button(left_layout, "每日準備 (Daily Prepare)", self.start_daily)
        self.add_task_button(left_layout, "怪物收藏 (Collection)", self.start_collection)
        self.add_task_button(left_layout, "每日 BOSS (Daily Boss)", self.start_boss)
        self.add_task_button(left_layout, "輸入倉庫密碼 (Storage)", self.start_storage)
        self.add_task_button(left_layout, "跳舞機 (Dancing)", self.start_dance)
        
        # 底部填充，把按鈕頂上去
        left_layout.addStretch()
        
        # 停止按鈕 (放在左側最下面，紅色)
        self.btn_stop = QPushButton("🔴 緊急停止 (STOP)")
        self.btn_stop.setMinimumHeight(50)
        # 注意：深色主題下紅色背景可能太亮，這裡稍微調暗一點，文字用白色
        self.btn_stop.setStyleSheet("background-color: #8B0000; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_stop.clicked.connect(self.stop_script)
        left_layout.addWidget(self.btn_stop)
        
        main_layout.addWidget(left_panel, 1) # 左側佔 1 等份
        
        # --- 右側 Log 面板 ---
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Log 標題列 (水平佈局：左邊標題，右邊清除按鈕)
        log_header_layout = QHBoxLayout()
        
        log_label = QLabel("執行日誌")
        log_label.setStyleSheet("font-weight: bold;")
        log_header_layout.addWidget(log_label)
        
        log_header_layout.addStretch() # 把按鈕推到最右邊
        
        # 清除按鈕
        self.btn_clear_log = QPushButton("🧹") # 掃把 Emoji
        self.btn_clear_log.setToolTip("清除日誌")
        self.btn_clear_log.setFixedSize(30, 30) # 設定為小方形
        self.btn_clear_log.clicked.connect(self.text_area_clear)
        log_header_layout.addWidget(self.btn_clear_log)
        
        right_layout.addLayout(log_header_layout)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        # 不需要手動設定字體顏色，主題引擎會處理
        self.text_area.setStyleSheet("font-family: Consolas, Monospace;")
        right_layout.addWidget(self.text_area)
        
        main_layout.addWidget(right_panel, 2) # 右側佔 2 等份
        
        # --- 初始化後端邏輯 ---
        # 建立信號橋樑
        self.log_signal = LogSignal()
        self.log_signal.text_written.connect(self.append_text)
        
        # 建立任務管家，把信號的發射方法傳給它
        self.manager = TaskManager(log_callback=self.log_signal.text_written.emit)

    def add_task_button(self, layout, text, slot):
        """輔助函數：建立並加入按鈕"""
        btn = QPushButton(text)
        btn.setMinimumHeight(40)
        btn.clicked.connect(slot)
        layout.addWidget(btn)
        return btn

    def text_area_clear(self):
        """清除日誌區域"""
        self.text_area.clear()

    @Slot(str)
    def append_text(self, text):
        """
        接收到 Log 信號時更新 UI
        """
        self.text_area.append(text)
        # 捲動到底部
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # --- 任務啟動函數 ---
    def start_grind(self):
        self.manager.start_task(MapleGrind, self.controller)

    def start_daily(self):
        self.manager.start_task(DailyPrepare, self.controller)

    def start_collection(self):
        self.manager.start_task(MonsterCollection, self.controller)

    def start_boss(self):
        self.manager.start_task(DailyBoss, self.controller)

    def start_storage(self):
        self.manager.start_task(Storage, self.controller)

    def start_dance(self):
        self.manager.start_task(Dancing, self.controller)

    def stop_script(self):
        """停止當前腳本"""
        self.manager.stop_task()

    def update_ui_state(self, running):
        """
        根據執行狀態切換按鈕的啟用/停用
        (這部分可以之後做得更細緻，目前先簡單處理)
        """
        pass
        # self.btn_grind.setEnabled(not running)
