import directkeys
import random

key_list = {"shift", "d", "pagedown", "end"}
def attack():
    key_press = random.choice(key_list)
    print(key_press)


if __name__ == "__main__":
    for i in range(10):
        attack()