import serial.tools.list_ports
import threading
from serial import Serial
import os


class DeviceNotFoundException(Exception):
    """
    找不到你要找的裝置
    """
    pass


class XiaoController:

    def __init__(self, baudrate=115200, timeout=0.001):
        self.__port = None
        self.__connection= None
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__serial_number = os.getenv("SERIAL_NUMBER")
        self.__stop_event = threading.Event()

    def _get_xiao_ports(self):
        ports = serial.tools.list_ports.comports()
        if self.__serial_number is not None:
            for port in ports:
                if port.serial_number == self.__serial_number:
                    return port.name
        raise DeviceNotFoundException("找不到xiao")

    def __enter__(self):
        self.__port = self._get_xiao_ports()
        try:
            self.__connection = Serial(port=self.__port, baudrate=self.__baudrate, timeout=self.__timeout)
            # 同時建立一個thread去聽Xiao回過來的訊息
            t = threading.Thread(target=self._read_from_port, daemon=True)
            t.start()
            print("連線成功！控制器已準備就緒。")
            return self
        except serial.SerialException as e:
            print(f'無法建立連線：{e}')
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        if exc_type:
            print(f"因異常退出: {exc_type.__name__}: {exc_val}")
        return False

    def _close(self):
        self.__stop_event.set()
        if self.__connection and self.__connection.is_open:
            self.__connection.close()
            print(f"連接埠 {self.__port} 已關閉。")
        self.__connection = None

    def __send(self, string: str):
        """
        向硬體發送一個按鍵指令
        :param string: 要傳送的東西
        """
        if not self.__connection:
            print("沒有建立連線")
            return None
        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(string.encode('utf-8'))
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def press_key(self, key: str):
        """
        向硬體發送一個按鍵指令
        :param key: 要按的按鈕
        """
        self.__send(f'{key}\n')
        print(f"已發送指令: 按下 {key}")


    def key_down(self, key: str):
        """
        向硬體發送一個長壓按鍵指令
        :param key: 要長壓的按鈕
        """
        self.__send(f'keyDown:{key}\n')
        print(f"已發送指令: 長壓 {key}")

    def key_up(self, key: str):
        """
        向硬體發送一個放開按鍵指令
        :param key: 要放開的按鈕
        """
        self.__send(f'keyUp:{key}\n')
        print(f"已發送指令: 放開 {key}")

    def scroll_up(self):
        """
        向硬體發送一個滑鼠滾輪上滑指令
        """
        self.__send(f'scroll_up\n')
        print(f"已發送指令: 要上滑")

    def scroll_down(self):
        """
        向硬體發送一個滑鼠滾輪下滑指令
        """
        self.__send(f'scroll_down\n')
        print(f"已發送指令: 要下滑")

    def send_mouse_location(self, location: tuple):
        """
        向硬體發送一個按鍵指令
        :param location: 滑鼠和目標之間的距離差
        """
        self.__send(f'{location}\n')
        print(f"已發送指令: 要移動'{location}'")

    def click(self):
        """
        向硬體發送一個按下滑鼠的指令
        """
        self.__send(f'click\n')
        print(f"已發送指令：按下滑鼠")

    def release_all(self):
        """
        向硬體發送一個放開所有按壓的按鍵的指令
        """
        self.__send(f'release_all\n')
        print(f"已發送指令: 放開全部按鍵")

    def _read_from_port(self):
        while not self.__stop_event.is_set():
            if self.__connection is not None and self.__connection.is_open:
                data = self.__connection.readline()
                if data:
                    print("Xiao:", data.decode().strip())
            else:
                break


if __name__ == "__main__":
    with XiaoController() as controller:
        controller.press_key("a")
