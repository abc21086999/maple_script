import time
from pynput import keyboard
from src.MapleScript import MapleScript

class RouteRecorder(MapleScript):
    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller, log_callback)
        self.events = []
        self.start_time = None

    def start(self):
        """
        任務入口：由 TaskManager 在背景執行緒中呼叫
        """
        self.log("=== 路徑錄製啟動 ===")
        self.log("請切換至遊戲視窗開始操作。")
        self.log("點擊 UI 的 [STOP] 按鈕結束錄製。")

        self.events = []
        self.start_time = time.time()

        # 啟動 pynput 監聽器
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            # 持續檢查是否應該繼續執行 (由 UI 控制) 以及監聽器是否還在運行
            while self.should_continue() and listener.running:
                # 使用 MapleScript 提供的可中斷 sleep
                if self.sleep(0.1):
                    break
            
            # 如果是點擊 UI 停止，手動關閉監聽器
            if listener.running:
                listener.stop()

        self.save_route()
        self.log("=== 路徑錄製結束 ===")

    def _get_key_str(self, key):
        """
        將 pynput 的 Key 物件轉換為與 XiaoController 相容的字串代碼
        """
        # 一般字元鍵 (a, b, c...)
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        
        # 特殊功能鍵 (space, ctrl, shift...)
        if hasattr(key, 'name'):
            # pynput 的 name 與 XiaoCode 的指令可能有差異，這裡做轉換
            key_mapping = {
                'page_up': 'pageup',
                'page_down': 'pagedown',
                'ctrl_l': 'ctrl',
                'ctrl_r': 'r_ctrl',
                'alt_l': 'alt',
                'alt_r': 'r_alt',
                'shift_l': 'shift',
                'shift_r': 'r_shift',
            }
            
            # 如果在 mapping 裡就用轉換後的，否則直接用原名 (如 'f1', 'enter', 'space' 等是一樣的)
            return key_mapping.get(key.name, key.name)
            
        return None

    def on_press(self, key):
        """鍵盤按下回調"""
        if self.start_time is None:
            return

        key_str = self._get_key_str(key)
        if key_str:
            elapsed = round(time.time() - self.start_time, 3)
            self.events.append({
                'action': 'key_down',
                'key': key_str,
                'time': elapsed
            })

    def on_release(self, key):
        """鍵盤放開回調"""
        if self.start_time is None:
            return

        key_str = self._get_key_str(key)
        if key_str:
            elapsed = round(time.time() - self.start_time, 3)
            self.events.append({
                'action': 'key_up',
                'key': key_str,
                'time': elapsed
            })

    def save_route(self):
        """將錄製到的事件寫入設定檔"""
        if not self.events:
            self.log("警告：沒有錄製到任何動作，不進行儲存。")
            return

        try:
            # 改用 SettingsManager 儲存 (會自動存為 JSON 並處理路徑)
            self.settings.save("recorded_route", self.events)
            self.log(f"成功錄製 {len(self.events)} 個動作。")
        except Exception as e:
            self.log(f"儲存路徑檔案時發生錯誤: {e}")
