import serial.tools.list_ports
import threading
from serial import Serial


class DeviceNotFoundException(Exception):
    """
    找不到你要找的裝置
    """
    pass


class XiaoController:
    XIAO_SERIAL_NUMBER = "CCAB7951D342"

    def __init__(self, baudrate=115200, timeout=0.01):
        self.__port = None
        self.__connection= None
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__stop_event = threading.Event()

    def _get_xiao_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.serial_number == self.XIAO_SERIAL_NUMBER:
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

    def press_key(self, key: str):
        """
        向硬體發送一個按鍵指令
        :param key: 要按的按鈕
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'{key}\n'.encode('utf-8'))
            print(f"已發送指令: 按下 {key}")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def key_down(self, key: str):
        """
        向硬體發送一個長壓按鍵指令
        :param key: 要長壓的按鈕
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'keyDown:{key}\n'.encode('utf-8'))
            print(f"已發送指令: 長壓 {key}")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def key_up(self, key: str):
        """
        向硬體發送一個放開按鍵指令
        :param key: 要放開的按鈕
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'keyUp:{key}\n'.encode('utf-8'))
            print(f"已發送指令: 放開 {key}")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def scroll_up(self):
        """
        向硬體發送一個滑鼠滾輪上滑指令
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'scroll_up\n'.encode('utf-8'))
            print(f"已發送指令: 要上滑")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def scroll_down(self):
        """
        向硬體發送一個滑鼠滾輪下滑指令
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'scroll_down\n'.encode('utf-8'))
            print(f"已發送指令: 要下滑")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def send_mouse_location(self, location: tuple):
        """
        向硬體發送一個按鍵指令
        :param location: 滑鼠和目標之間的距離差
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'{location}\n'.encode('utf-8'))
            print(f"已發送指令: 要移動'{location}'")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

    def click(self):
        """
        向硬體發送一個按下滑鼠的指令
        """
        if not self.__connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.__connection.write(f'click\n'.encode('utf-8'))
            print(f"已發送指令：按下滑鼠")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self._close()
            raise

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
        print(controller.port)
        controller.press_key("a")
