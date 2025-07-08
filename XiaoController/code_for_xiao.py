import time
import usb_hid
import usb_cdc

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# 建立 HID 鍵盤物件
keyboard = Keyboard(usb_hid.devices)
serial = usb_cdc.console

# Keycode 對應表，根據你實際會發的字來擴充
KEY_MAP = {
    # 用單個 ASCII 字元作為 key
    '1': Keycode.PAGE_DOWN,   # "漩渦球球"
    '2': Keycode.SHIFT,       # "艾爾達斯降臨"
    '3': Keycode.END,         # "風轉奇想"
    '4': Keycode.QUOTE,       # "小雞"
    '5': Keycode.D,           # "龍捲風"
    '6': Keycode.B,           # "季風"
    '7': Keycode.F,           # "蜘蛛之鏡"
    '8': Keycode.F5,          # "烈陽印記"
    '9': Keycode.SIX,         # "西爾芙之壁"
    'a': Keycode.F2,          # "武公"
    'b': Keycode.F1,          # "一鍵爆發"
    'c': Keycode.V,           # "阿涅摩依"
    'u': Keycode.UP_ARROW,    # "向上移動"
    ']': Keycode.RIGHT_BRACKET, # 展開技能快捷
}

print("XIAO 已啟動，等待指令...")
print(f"usb_cdc.data is None? {usb_cdc.console is None}")
print(serial.in_waiting)
# 開始監聽 usb_cdc 的 data channel（用來收電腦發來的字串）
while True:
    # 如果有資料就讀一行
    if serial.in_waiting:
        try:
            line = serial.readline()             # 讀到 '\n' 為止
            key_str = line.decode().strip().lower()
            print(f"收到：{key_str}")

            if key_str in KEY_MAP:
                keycode = KEY_MAP[key_str]
                keyboard.press(keycode)
                time.sleep(0.05)
                keyboard.release(keycode)
            else:
                print(f"未知指令：{key_str}")

        except Exception as e:
            print(f"處理指令錯誤：{e}")

    time.sleep(0.01)
