from functions import *


switch_to_maple()

while True:
    time.sleep(1)
    if random.random() < 0.5:
        pydirectinput.press("up")
