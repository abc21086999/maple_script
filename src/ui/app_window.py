from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QLabel, QFrame, QMessageBox)
from PySide6.QtCore import Signal, QObject, Slot, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from src.ui.task_manager import TaskManager
from src.utils.settings_manager import SettingsManager
from src.ui.settings_dialog import SettingsDialog
from src.ui.grind_settings_dialog import GrindSettingsDialog
from src.ui.storage_settings_dialog import StorageSettingsDialog
from src.ui.hardware_setup_dialog import HardwareSetupDialog
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
        
        # 1. 基礎視窗設定
        self.setWindowTitle("Automation Control Center")
        self.resize(900, 600)
        self.setWindowIcon(self._create_emoji_icon("🤖"))
        
        # 2. 初始化 UI 排版
        self._setup_ui()
        
        # 3. 初始化後端邏輯與信號連接
        self._setup_backend()

    def _setup_ui(self):
        """初始化主要的 UI 佈局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        
        self._setup_left_panel()
        self._setup_right_panel()

    def _setup_left_panel(self):
        """建立左側控制面板"""
        left_panel = QFrame()
        layout = QVBoxLayout(left_panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 標題
        title = QLabel("任務選擇")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 任務按鈕群
        self._add_task_button(layout, "開始練功 (Grind)", self.start_grind, self.open_grind_settings)
        self._add_task_button(layout, "每日準備 (Daily Prepare)", self.start_daily, self.open_daily_settings)
        self._add_task_button(layout, "怪物收藏 (Collection)", self.start_collection)
        self._add_task_button(layout, "輸入倉庫密碼 (Storage)", self.start_storage, self.open_storage_settings)
        # self._add_task_button(layout, "每日 BOSS (Daily Boss)", self.start_boss)
        # self._add_task_button(layout, "跳舞機 (Dancing)", self.start_dance)

        layout.addStretch()

        # 硬體設定按鈕
        self.btn_hardware = QPushButton("🔌 硬體連線設定")
        self.btn_hardware.setMinimumHeight(40)
        self.btn_hardware.clicked.connect(self.open_hardware_settings)
        layout.addWidget(self.btn_hardware)
        
        # 停止按鈕 (具備 Hover 與 Pressed 效果)
        self.btn_stop = QPushButton("🔴 緊急停止 (STOP)")
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #8B0000; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #A52A2A;
            }
            QPushButton:pressed {
                background-color: #600000;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_script)
        layout.addWidget(self.btn_stop)
        
        self.main_layout.addWidget(left_panel, 1)

    def _setup_right_panel(self):
        """建立右側日誌面板"""
        right_panel = QFrame()
        layout = QVBoxLayout(right_panel)
        
        # Log 標題列
        header_layout = QHBoxLayout()
        log_label = QLabel("執行日誌")
        log_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(log_label)
        header_layout.addStretch()
        
        btn_clear = QPushButton("🧹")
        btn_clear.setToolTip("清除日誌")
        btn_clear.setFixedSize(30, 30)
        btn_clear.clicked.connect(self.text_area_clear)
        header_layout.addWidget(btn_clear)
        
        layout.addLayout(header_layout)
        
        # 文字區
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.document().setMaximumBlockCount(1000)
        self.text_area.setStyleSheet("font-family: Consolas, Monospace;")
        layout.addWidget(self.text_area)
        
        self.main_layout.addWidget(right_panel, 2)

    def _setup_backend(self):
        """初始化 TaskManager 與信號傳遞機制"""
        # 初始化設定管理器
        self.settings_manager = SettingsManager()

        # 建立跨執行緒傳話筒 (Signal)
        self.log_signal = LogSignal()
        self.log_signal.text_written.connect(self.append_text)
        
        # 建立任務管家
        self.manager = TaskManager(log_callback=self.log_signal.text_written.emit)

    def _add_task_button(self, layout, text, slot, settings_slot=None):
        """輔助函數：建立並加入按鈕，可選配設定按鈕"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主要任務按鈕
        btn = QPushButton(text)
        btn.setMinimumHeight(40)
        btn.clicked.connect(slot)
        row_layout.addWidget(btn, stretch=1) # 讓主按鈕佔據大部分空間
        
        # 設定按鈕 (如果有的話)
        if settings_slot:
            settings_btn = QPushButton("⚙️")
            settings_btn.setToolTip("設定")
            settings_btn.setFixedSize(40, 40)
            settings_btn.clicked.connect(settings_slot)
            row_layout.addWidget(settings_btn)
            
        layout.addLayout(row_layout)

    def _create_emoji_icon(self, emoji: str) -> QIcon:
        """將 Emoji 繪製成 QIcon"""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("transparent"))
        painter = QPainter(pixmap)
        font = QFont("Segoe UI Emoji", int(size * 0.8))
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        return QIcon(pixmap)

    def text_area_clear(self):
        """清除日誌區域"""
        self.text_area.clear()

    @Slot(str)
    def append_text(self, text):
        """接收到 Log 信號時更新 UI"""
        self.text_area.append(text)
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # --- 任務啟動函數 ---
    def start_grind(self):
        self.manager.start_task(MapleGrind, self.controller)

    def open_grind_settings(self):
        """開啟練功的設定視窗"""
        # 傳入 manager 和 controller 以供錄製功能使用
        dialog = GrindSettingsDialog(self, self.settings_manager, self.manager, self.controller)
        if dialog.exec():
            self.log_signal.text_written.emit("練功技能設定已更新")

    def open_daily_settings(self):
        """開啟每日任務的設定視窗"""
        dialog = SettingsDialog(self, self.settings_manager, "daily_prepare", "每日準備設定")
        if dialog.exec(): # 如果使用者按下確定
            dialog.save_settings() # 儲存設定
            self.log_signal.text_written.emit("設定已更新")

    def start_daily(self):
        # DailyPrepare 會自動讀取設定檔決定要跑哪些任務
        self.manager.start_task(DailyPrepare, self.controller)

    def start_collection(self):
        self.manager.start_task(MonsterCollection, self.controller)

    def start_boss(self):
        self.manager.start_task(DailyBoss, self.controller)

    def open_storage_settings(self):
        """開啟倉庫密碼的設定視窗"""
        dialog = StorageSettingsDialog(self)
        dialog.exec()

    def start_storage(self):
        self.manager.start_task(Storage, self.controller)

    def start_dance(self):
        self.manager.start_task(Dancing, self.controller)

    def open_hardware_settings(self):
        """開啟硬體設定視窗"""
        dialog = HardwareSetupDialog(self.settings_manager, self)
        if dialog.exec() == HardwareSetupDialog.Accepted:
            QMessageBox.information(self, "設定已儲存", "硬體設定已更新！\n由於硬體連線在啟動時建立，請重啟程式以套用新設定。")

    def stop_script(self):
        """停止當前腳本"""
        self.manager.stop_task()