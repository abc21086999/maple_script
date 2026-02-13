import serial.tools.list_ports
import threading
from serial import Serial
from src.utils.settings_manager import SettingsManager


# 定義已知廠商的 VID 對照表
VID_MAPPING = {
    0x2886: "Seeed Studio",
    0x239A: "Adafruit",
    0x2E8A: "Raspberry Pi",
    0x2341: "Arduino SA",
    0x303A: "Espressif Systems",
    0x0483: "STMicroelectronics",
    0x04D8: "Microchip Technology Inc.",
    0x1915: "Nordic Semiconductor",
    0x10C4: "Silicon Labs",
    0x0D28: "micro:bit / community",
    0x1A86: "QinHeng Electronics",
}


class DeviceNotFoundException(Exception):
    """
    找不到你要找的裝置
    """
    pass


class XiaoController:

    def __init__(self, baudrate=115200, timeout=0.001):
        self.__port = None
        self.__connection = None
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__stop_event = threading.Event()

    @staticmethod
    def list_available_ports():
        """
        列出系統中所有可用的 COM Ports，並回傳詳細資訊列表。
        """
        results = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            vendor = VID_MAPPING.get(port.vid, "Unknown")
            info = {
                "port": port.device,
                "description": port.description,
                "vendor": vendor,
                "serial_number": port.serial_number
            }
            results.append(info)
        return results

    def _get_xiao_ports(self):
        """
        根據設定檔中的序號尋找對應的 COM Port
        """
        serial_number = SettingsManager().get("hardware", "serial_number")

        if not serial_number:
            raise DeviceNotFoundException("尚未設定硬體序號")

        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.serial_number == serial_number:
                return port.name
        
        raise DeviceNotFoundException(f"找不到序號為 {serial_number} 的裝置")

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
                try:
                    data = self.__connection.readline()
                    if data:
                        print("Xiao:", data.decode().strip())
                except Exception:
                    break
            else:
                break

class ControllerMocker:
    """
    硬體控制器的 Mock 類別，用於在沒有硬體時維持程式運行。
    """
    pass


if __name__ == "__main__":
    with XiaoController() as controller:
        controller.press_key("a")
