import time
import usb_hid
import usb_cdc

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# 建立 HID 鍵盤物件
keyboard = Keyboard(usb_hid.devices)
serial = usb_cdc.console

# Keycode 對應表，根據你實際會發的字來擴充
mapping = {
    # 用單個 ASCII 字元作為 key
    'pagedown': Keycode.PAGE_DOWN,  # "漩渦球球"
    'shift': Keycode.SHIFT,  # "艾爾達斯降臨"
    'end': Keycode.END,  # "風轉奇想"
    "'": Keycode.QUOTE,  # "小雞"
    'd': Keycode.D,  # "龍捲風"
    'b': Keycode.B,  # "季風"
    'f': Keycode.F,  # "蜘蛛之鏡"
    'f5': Keycode.F5,  # "烈陽印記"
    '6': Keycode.SIX,  # "西爾芙之壁"
    'f2': Keycode.F2,  # "武公"
    'f1': Keycode.F1,  # "一鍵爆發"
    'v': Keycode.V,  # "阿涅摩依"
    'up': Keycode.UP_ARROW,  # "向上移動"
    ']': Keycode.RIGHT_BRACKET,  # "展開技能快捷"
}

print("XIAO 已啟動，等待指令...")
print(f"usb_cdc.data is None? {usb_cdc.console is None}")
print(serial.in_waiting)
# 開始監聽 usb_cdc 的 data channel（用來收電腦發來的字串）
while True:
    # 如果有資料就讀一行
    if serial.in_waiting:
        try:
            line = serial.readline()  # 讀到 '\n' 為止
            key_str = line.decode().strip().lower()
            print(f"收到：{key_str}")
            keycode = mapping.get(key_str)

            if keycode:
                keyboard.press(keycode)
                time.sleep(0.05)
                keyboard.release(keycode)
                print(f'已按下：{key_str}')
            else:
                print(f"未知指令：{key_str}")

        except Exception as e:
            print(f"處理指令錯誤：{e}")

    time.sleep(0.01)
