import time

import serial.tools.list_ports
import threading


class DeviceNotFoundException(Exception):
    """
    找不到你要找的裝置
    """
    pass


class XiaoController:
    XIAO_SERIAL_NUMBER = "CCAB7951D342"

    def __init__(self, baudrate=115200, timeout=0.01):
        self.port = None
        self.connection= None
        self.baudrate = baudrate
        self.timeout = timeout

    def _get_xiao_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.serial_number == self.XIAO_SERIAL_NUMBER:
                return port.name
        raise DeviceNotFoundException("找不到xiao")

    def __enter__(self):
        self.port = self._get_xiao_ports()
        try:
            self.connection = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            # 同時建立一個thread去聽Xiao回過來的訊息
            t = threading.Thread(target=self.read_from_port, daemon=True)
            t.start()
            print("連線成功！控制器已準備就緒。")
            return self
        except serial.SerialException as e:
            print(f'無法建立連線：{e}')
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            print(f"因異常退出: {exc_type.__name__}: {exc_val}")
        return False

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"連接埠 {self.port} 已關閉。")
        self.connection = None

    def press_key(self, key: str):
        """
        向硬體發送一個按鍵指令
        :param key: 要按的按鈕
        """
        if not self.connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.connection.write(f'{key}\n'.encode('utf-8'))
            print(f"已發送指令: press '{key}'")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self.close()
            raise

    def send_mouse_location(self, location: tuple):
        """
        向硬體發送一個按鍵指令
        :param location: 滑鼠要移動過去的位置
        """
        if not self.connection:
            print("沒有建立連線")
            return None

        try:
            # 字串需要被編碼成位元組 (bytes) 才能透過序列埠傳輸
            self.connection.write(f'{location}\n'.encode('utf-8'))
            print(f"已發送指令: press '{location}'")
        except serial.SerialException as e:
            print(f'發生錯誤：{e}')
            self.close()
            raise

    def read_from_port(self):
        while True:
            if self.connection.is_open:
                data = self.connection.readline()
                if data:
                    print("Xiao:", data.decode().strip())
            else:
                break


if __name__ == "__main__":
    with XiaoController() as controller:
        print(controller.port)
        controller.press_key("a")
