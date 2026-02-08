from src.MapleScript import MapleScript
from src.utils.xiao_controller import XiaoController
from src.utils.secret_manager import SecretManager


class Storage(MapleScript):

    def __init__(self, controller=None, log_callback=None):
        super().__init__(controller=controller, log_callback=log_callback)
        self.__icon_dict, self.__ui_dict = self.yaml_loader.storage_resources
        self.__second_password = SecretManager.get_storage_password()
        self.__storage_ui_title = self.__ui_dict['title']
        self.__storage_icon = self.__ui_dict['icon']
        self.__inventory = self.__ui_dict['inventory']
        self.__upper_case = self.__ui_dict['upper_case_button']
        self.__isupper = False

    def __click_button(self, char: str):
        char_pic = self.__icon_dict.get(char)
        # 如果不在畫面上...大膽假設就是被我們的滑鼠擋住了
        if not self.is_on_screen(char_pic):
            self.click()
        else:
            self.find_and_click_image(char_pic)

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

        # 如果畫面上沒有輸入第二組密碼的UI，那就打開倉庫界面
        if not self.is_on_screen(self.__storage_ui_title):
            if not self.is_on_screen(pic = self.__inventory):
                self.invoke_menu()
                self.press_and_wait(["tab", "right", "down", "down", "enter"])
        self.find_and_click_image(self.__storage_icon)

        # 等待界面出現
        while self.should_continue() and not self.is_on_screen(self.__storage_ui_title):
            self.sleep(0.3)

        # 將密碼一個一個輸入
        for password_char in self.__second_password:
            # 如果這個字是大寫，但是大寫沒開，那就打開，然後輸入
            if password_char.isupper() and not self.__isupper:
                self.find_and_click_image(self.__upper_case)
                self.__isupper = True
                self.__click_button(password_char)
            # 如果這個字不是大寫，但是大寫卻開了，那就關掉，然後輸入
            elif password_char.islower() and self.__isupper:
                self.find_and_click_image(self.__upper_case)
                self.__isupper = False
                self.__click_button(password_char)
            # 剩下包括：大寫且大寫開了、小寫大寫也沒開、數字，都直接輸入
            else:
                self.__click_button(password_char)

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
