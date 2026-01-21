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
    # --- 字母 (Letters) ---
    'a': Keycode.A,
    'b': Keycode.B,
    'c': Keycode.C,
    'd': Keycode.D,
    'e': Keycode.E,
    'f': Keycode.F,
    'g': Keycode.G,
    'h': Keycode.H,
    'i': Keycode.I,
    'j': Keycode.J,
    'k': Keycode.K,
    'l': Keycode.L,
    'm': Keycode.M,
    'n': Keycode.N,
    'o': Keycode.O,
    'p': Keycode.P,
    'q': Keycode.Q,
    'r': Keycode.R,
    's': Keycode.S,
    't': Keycode.T,
    'u': Keycode.U,
    'v': Keycode.V,
    'w': Keycode.W,
    'x': Keycode.X,
    'y': Keycode.Y,
    'z': Keycode.Z,

    # --- 主鍵盤區數字 (Top Row Numbers) ---
    '0': Keycode.ZERO,
    '1': Keycode.ONE,
    '2': Keycode.TWO,
    '3': Keycode.THREE,
    '4': Keycode.FOUR,
    '5': Keycode.FIVE,
    '6': Keycode.SIX,
    '7': Keycode.SEVEN,
    '8': Keycode.EIGHT,
    '9': Keycode.NINE,

    # --- 功能鍵 (F-Keys) ---
    'f1': Keycode.F1,
    'f2': Keycode.F2,
    'f3': Keycode.F3,
    'f4': Keycode.F4,
    'f5': Keycode.F5,
    'f6': Keycode.F6,
    'f7': Keycode.F7,
    'f8': Keycode.F8,
    'f9': Keycode.F9,
    'f10': Keycode.F10,
    'f11': Keycode.F11,
    'f12': Keycode.F12,
    # 註：F13-F24 雖然在 API 中，但實體鍵盤罕見，故預設列到 F12

    # --- 常用控制鍵 (Common Controls) ---
    'enter': Keycode.ENTER,
    'esc': Keycode.ESCAPE,
    'backspace': Keycode.BACKSPACE,
    'tab': Keycode.TAB,
    'space': Keycode.SPACE,
    'menu': Keycode.APPLICATION, # 右邊 Ctrl 旁邊那個選單鍵

    # --- 編輯與導航鍵 (Navigation & Editing) ---
    'insert': Keycode.INSERT,
    'delete': Keycode.DELETE,
    'home': Keycode.HOME,
    'end': Keycode.END,
    'pageup': Keycode.PAGE_UP,
    'pagedown': Keycode.PAGE_DOWN,
    'up': Keycode.UP_ARROW,
    'down': Keycode.DOWN_ARROW,
    'left': Keycode.LEFT_ARROW,
    'right': Keycode.RIGHT_ARROW,

    # --- 修飾鍵 (Modifiers - Win鍵已排除) ---
    'shift': Keycode.SHIFT,        # 左 Shift
    'ctrl': Keycode.CONTROL,       # 左 Ctrl
    'alt': Keycode.ALT,            # 左 Alt (Option)
    'r_shift': Keycode.RIGHT_SHIFT,
    'r_ctrl': Keycode.RIGHT_CONTROL,
    'r_alt': Keycode.RIGHT_ALT,

    # --- 符號鍵 (Symbols) ---
    '-': Keycode.MINUS,            # - 和 _
    '=': Keycode.EQUALS,           # = 和 +
    '[': Keycode.LEFT_BRACKET,     # [ 和 {
    ']': Keycode.RIGHT_BRACKET,    # ] 和 }
    '\\': Keycode.BACKSLASH,       # \ 和 |
    ';': Keycode.SEMICOLON,        # ; 和 :
    "'": Keycode.QUOTE,            # ' 和 "
    '`': Keycode.GRAVE_ACCENT,     # ` 和 ~
    ',': Keycode.COMMA,            # , 和 <
    '.': Keycode.PERIOD,           # . 和 >
    '/': Keycode.FORWARD_SLASH,    # / 和 ?
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
    print(f'已經移動({dx}, {dy})')


def click_mouse():
    mouse.click(Mouse.LEFT_BUTTON)
    mouse.release_all()
    print(f'已經按下滑鼠左鍵後放開')


def keyDown(decoded_string: str):
    keyDown, key = decoded_string.split(":")
    keycode = mapping.get(key)
    if keycode is not None:
        keyboard.press(keycode)
        print(f'已長壓：{decoded_string}')
    else:
        print(f"未知指令：{decoded_string}")


def keyUp(decoded_string: str):
    keyDown, key = decoded_string.split(":")
    keycode = mapping.get(key)
    if keycode is not None:
        keyboard.release(keycode)
        print(f'已放開：{decoded_string}')
    else:
        print(f"未知指令：{decoded_string}")

def release_all():
    keyboard.release_all()
    mouse.release_all()


def scroll_up():
    mouse.move(wheel=1)


def scroll_down():
    mouse.move(wheel=-1)


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

            # 如果是keyDown開頭，那就是要下壓某個按鍵
            elif decoded_str.startswith("keydown"):
                keyDown(decoded_str)

            # 如果是keyUp開頭，那就是要下壓某個按鍵
            elif decoded_str.startswith("keyup"):
                keyUp(decoded_str)

            # 如果是scroll_up，那就是要上滑
            elif decoded_str == "scroll_up":
                scroll_up()

            # 如果是scroll_down，那就是要下滑
            elif decoded_str == "scroll_down":
                scroll_down()

            # 如果是release_all，那就要把全部的按鍵都放開
            elif decoded_str == "release_all":
                release_all()

            # 此外的都是要按下的按鍵
            else:
                print(f"收到：{decoded_str}")
                handle_keyboard(decoded_str)

        except Exception as e:
            print(f"處理指令錯誤：{e}")

