import time
import usb_hid
import usb_cdc

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode

# 建立 HID 鍵盤物件
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
serial = usb_cdc.console

# Keycode 對應表，根據你實際會發的字來擴充
mapping = {
    # 用單個 ASCII 字元作為 key
    'pagedown': Keycode.PAGE_DOWN,   # "漩渦球球"
    'shift': Keycode.SHIFT,          # "艾爾達斯降臨"
    'end': Keycode.END,              # "風轉奇想"
    "'": Keycode.QUOTE,              # "小雞"
    'd': Keycode.D,                  # "龍捲風"
    'b': Keycode.B,                  # "季風"
    'f': Keycode.F,                  # "蜘蛛之鏡"
    'f5': Keycode.F5,                # "烈陽印記"
    '6': Keycode.SIX,                # "西爾芙之壁"
    'f2': Keycode.F2,                # "武公"
    'f1': Keycode.F1,                # "一鍵爆發"
    'v': Keycode.V,                  # "阿涅摩依"
    'up': Keycode.UP_ARROW,          # "向上移動"
    ']': Keycode.RIGHT_BRACKET,      # "展開技能快捷"
    'f11': Keycode.F11,              # "角色預設鍵"
    'enter': Keycode.ENTER,          # "Enter鍵"
    'f10': Keycode.F10,              # "戰地聯盟界面"
    'esc': Keycode.ESC,              # "ESC按鍵"
}


def handle_keyboard(decoded_string: str):
    keycode = mapping.get(decoded_string)
    if keycode is not None:
        keyboard.press(keycode)
        time.sleep(0.05)
        keyboard.release(keycode)
        print(f'已按下：{decoded_string}')
    else:
        print(f"未知指令：{decoded_string}")


def handle_mouse(mouse_location: str):
    parts = mouse_location.strip("()").split(",")
    dx, dy = tuple(int(p.strip()) for p in parts)
    mouse.move(x=dx, y=dy)


def click_mouse():
    mouse.click(Mouse.LEFT_BUTTON)
    mouse.release_all()


print("XIAO 已啟動，等待指令...")
print(f"usb_cdc.data is None? {usb_cdc.console is None}")
print(serial.in_waiting)

# 開始監聽 usb_cdc 的 data channel（用來收電腦發來的字串）
while True:
    # 如果有資料就讀一行
    if serial.in_waiting:
        try:
            line = serial.readline()  # 讀到 '\n' 為止
            decoded_str = line.decode().strip().lower()

            # 如果收到的字串當中，而且以左右括號作為開始和結束
            # 那麼一定是螢幕座標
            if decoded_str.startswith("(") and decoded_str.endswith(")"):
                handle_mouse(decoded_str)

            # 如果送來的是click，那麼就要按下滑鼠左鍵
            elif decoded_str == "click":
                click_mouse()

            # 此外的都是要按下的按鍵
            else:
                print(f"收到：{decoded_str}")
                handle_keyboard(decoded_str)

        except Exception as e:
            print(f"處理指令錯誤：{e}")

    time.sleep(0.01)