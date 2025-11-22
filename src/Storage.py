import os
import time
from src.MapleScript import MapleScript
from src.XiaoController import XiaoController


class Storage(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)
        self.__number_dict, self.__ui_dict = self.yaml_loader.storage_resources
        self.__second_password = os.getenv("SECOND_PASSWORD")

    def __fill_in_the_password(self):
        """
        填入第二組密碼
        :return: None
        """
        # 如果沒有第二組密碼，那就提前中止
        if self.__second_password is None:
            return

        storage_ui_title = self.__ui_dict['title']
        fast_travel_icon = self.__ui_dict['fast_travel']

        # 如果畫面上沒有輸入第二組密碼的UI，那就打開倉庫界面
        if not self.is_on_screen(storage_ui_title):
            if not self.is_on_screen(fast_travel_icon):
                print("找不到快速旅行的icon")
                pass
            else:
                self.find_and_click_image(fast_travel_icon)
                self.find_and_click_image(self.__ui_dict['icon'])

        # 等待界面出現
        while not self.is_on_screen(storage_ui_title):
            time.sleep(0.3)

        # 將密碼一個一個輸入
        for password_char in self.__second_password:
            password_char_pic = self.__number_dict.get(password_char)
            if not self.is_on_screen(password_char_pic):
                self.find_and_click_image(storage_ui_title)
            self.find_and_click_image(password_char_pic)

        # 點擊確認
        self.find_and_click_image(self.__ui_dict['confirm'])

    def start(self):
        self.__fill_in_the_password()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Storage(Xiao)
        Maple.start()
