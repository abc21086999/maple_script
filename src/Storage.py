import time
from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController
from src.utils.secret_manager import SecretManager


class Storage(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__number_dict, self.__ui_dict = self.yaml_loader.storage_resources
        self.__second_password = SecretManager.get_storage_password()

    def __fill_in_the_password(self):
        """
        填入第二組密碼
        :return: None
        """
        # 如果沒有第二組密碼，那就提前中止
        if self.__second_password is None:
            self.log("錯誤：未設定第二組密碼。請點擊主畫面 '輸入倉庫密碼' 旁的設定按鈕進行設定。")
            return
            
        if not self.should_continue(): return
        self.log("正在輸入倉庫密碼...")

        storage_ui_title = self.__ui_dict['title']
        storage_icon = self.__ui_dict['icon']
        inventory = self.__ui_dict['inventory']

        # 如果畫面上沒有輸入第二組密碼的UI，那就打開倉庫界面
        if not self.is_on_screen(storage_ui_title):
            if not self.is_on_screen(pic = inventory):
                self.press_and_wait("i", 0.5)
            self.find_and_click_image(storage_icon)

        # 等待界面出現
        while self.should_continue() and not self.is_on_screen(storage_ui_title):
            self.sleep(0.3)

        # 將密碼一個一個輸入
        for password_char in self.__second_password:
            if not self.should_continue():
                self.log("密碼輸入已中斷")
                return
                
            password_char_pic = self.__number_dict.get(password_char)
            if not self.is_on_screen(password_char_pic):
                self.find_and_click_image(storage_ui_title)
            self.find_and_click_image(password_char_pic)

        # 點擊確認
        if self.should_continue():
            self.find_and_click_image(self.__ui_dict['confirm'])
            self.log("密碼輸入完成")

    def start(self):
        self.__fill_in_the_password()


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = Storage(Xiao)
        Maple.start()
