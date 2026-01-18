from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTextEdit, QLabel, QFrame)
from PySide6.QtCore import Signal, QObject, Slot, Qt
from src.ui.task_manager import TaskManager
from src.MapleGrind import MapleGrind

class LogSignal(QObject):
    """
    用於跨執行緒發送 Log 訊息的信號類別
    """
    text_written = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.setWindowTitle("Guai Guai Automation Control Center")
        self.resize(800, 600)
        
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
        
        # 按鈕群
        self.btn_grind = QPushButton("開始練功 (Grind)")
        self.btn_grind.setMinimumHeight(40)
        self.btn_grind.clicked.connect(self.start_grind)
        left_layout.addWidget(self.btn_grind)
        
        # 可以預留其他按鈕的位置
        # self.btn_daily = QPushButton("每日任務 (Daily)")
        # left_layout.addWidget(self.btn_daily)
        
        # 底部填充，把按鈕頂上去
        left_layout.addStretch()
        
        # 停止按鈕 (放在左側最下面，紅色)
        self.btn_stop = QPushButton("🔴 緊急停止 (STOP)")
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setStyleSheet("background-color: #ffcccc; color: red; font-weight: bold;")
        self.btn_stop.clicked.connect(self.stop_script)
        left_layout.addWidget(self.btn_stop)
        
        main_layout.addWidget(left_panel, 1) # 左側佔 1 等份
        
        # --- 右側 Log 面板 ---
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        log_label = QLabel("執行日誌")
        log_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(log_label)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("font-family: Consolas, Monospace;")
        right_layout.addWidget(self.text_area)
        
        main_layout.addWidget(right_panel, 2) # 右側佔 2 等份
        
        # --- 初始化後端邏輯 ---
        # 建立信號橋樑
        self.log_signal = LogSignal()
        self.log_signal.text_written.connect(self.append_text)
        
        # 建立任務管家，把信號的發射方法傳給它
        self.manager = TaskManager(log_callback=self.log_signal.text_written.emit)

    @Slot(str)
    def append_text(self, text):
        """
        接收到 Log 信號時更新 UI
        """
        self.text_area.append(text)
        # 捲動到底部
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_grind(self):
        """啟動練功腳本"""
        self.manager.start_task(MapleGrind, self.controller)
        self.update_ui_state(running=True)

    def stop_script(self):
        """停止當前腳本"""
        self.manager.stop_task()
        self.update_ui_state(running=False)

    def update_ui_state(self, running):
        """
        根據執行狀態切換按鈕的啟用/停用
        (這部分可以之後做得更細緻，目前先簡單處理)
        """
        pass
        # self.btn_grind.setEnabled(not running)
