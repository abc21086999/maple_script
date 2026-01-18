import threading
import time

class TaskManager:
    def __init__(self, log_callback):
        self.current_thread = None
        self.current_script = None
        self.log_callback = log_callback

    def start_task(self, task_class, controller, *args, **kwargs):
        """
        啟動一個新的任務
        :param task_class: 要執行的類別 (例如 MapleGrind)
        :param controller: 硬體控制器
        """
        # 1. 如果已經有任務在跑，就不要再啟動新的
        if self.is_running():
            self.log_callback("錯誤：已有任務正在執行中！")
            return

        # 2. 建立並啟動執行緒，將實例化工作移至背景執行
        # 我們把所有需要的參數都傳給 _run_wrapper
        self.current_thread = threading.Thread(
            target=self._run_wrapper,
            args=(task_class, controller) + args,
            kwargs=kwargs
        )
        self.current_thread.daemon = True # 設為守護執行緒
        self.current_thread.start()

    def _run_wrapper(self, task_class, controller, *args, **kwargs):
        """
        這是一個包裝器，用來捕捉腳本執行時可能發生的錯誤，
        並確保執行結束後清理狀態。
        """
        try:
            # 在背景執行緒中進行實例化
            self.log_callback(f"正在初始化任務: {task_class.__name__}...")
            self.current_script = task_class(controller, log_callback=self.log_callback, *args, **kwargs)
            
            # 開始執行
            self.log_callback(f"任務啟動: {task_class.__name__}")
            self.current_script.start()
            
        except Exception as e:
            self.log_callback(f"任務執行失敗: {e}")
            # 對於預期的錯誤 (如找不到視窗)，不需要印出完整 traceback
            if not isinstance(e, RuntimeError):
                import traceback
                traceback.print_exc()
        finally:
            self.log_callback("任務結束")
            self.current_script = None
            self.current_thread = None

    def stop_task(self):
        """
        停止當前任務
        """
        if self.current_script:
            self.log_callback("正在嘗試停止任務...")
            self.current_script.stop()
        else:
            self.log_callback("目前沒有正在執行的任務")

    def is_running(self):
        """檢查是否有任務正在執行"""
        return self.current_thread is not None and self.current_thread.is_alive()
