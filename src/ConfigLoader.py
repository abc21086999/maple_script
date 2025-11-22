import yaml
from pathlib import Path
import PIL.Image
from functools import cached_property


class YamlLoader:

    def __init__(self):
        self.__config_path = Path(__file__).resolve().parent.parent / "config" / "config.yaml"
        self.__grind_routes_path = Path(__file__).resolve().parent.parent / "config" / "grind_routes.yaml"
        self.__photo_path = Path(__file__).resolve().parent.parent / 'photos'
    
    @cached_property
    def __config(self):
        """
        讀取YAML檔案
        """
        with open(self.__config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    @cached_property
    def grind_routes(self):
        """
        讀取練功路徑的YAML檔案
        """
        with open(self.__grind_routes_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    @cached_property
    def grind_setting(self):
        """
        提供練功相關的設定
        """
        return tuple(self.__config['grind_settings']['skill_gap_time'])

    @cached_property
    def skill_dict(self):
        """
        動態建立並回傳包含 PIL.Image 物件的技能字典
        """
        skills_dict = {}
        skills_config = self.__config['skills']

        for skill_name, skill_data in skills_config.items():
            image_path = self.__photo_path / skill_data['image']
            skills_dict[skill_name] = {
                'key': skill_data['key'],
                'image': PIL.Image.open(image_path)
            }
        return skills_dict

    @cached_property
    def boss_dict(self) -> dict:
        """
        建立並回傳每日行事曆當中每日Boss的圖片列表
        """
        boss_config = self.__config["boss"]
        boss_dict = {}

        for boss_name, boss_tab_pic in boss_config.items():
            img_path = self.__photo_path / "boss" / boss_tab_pic
            boss_dict[boss_name] = PIL.Image.open(img_path)

        return boss_dict

    @cached_property
    def storage_dict(self) -> dict:
        """
        建立並回傳倉庫UI的號碼和圖片
        """
        storage_config = self.__config["storage"]
        storage_dict = {}

        for number, num_pic in storage_config.items():
            img_path = self.__photo_path / "storage" / num_pic
            storage_dict[number] = PIL.Image.open(img_path)

        return storage_dict

    @cached_property
    def dancing_config(self) -> tuple[dict, dict]:
        """
        建立並回傳跳舞機活動的方向和圖片
        """
        dancing_config = self.__config["dancing"]
        dancing_dict = {}

        for direction, pic in dancing_config.items():
            img_path = self.__photo_path / "dancing" / pic
            dancing_dict[direction] = PIL.Image.open(img_path)

        dancing_ui_config = self.__config["dancing_ui"]
        dancing_ui_dict = dict()

        for ui, ui_pic in dancing_ui_config.items():
            img_path = self.__photo_path / "dancing" / ui_pic
            dancing_ui_dict[ui] = img_path

        return dancing_dict, dancing_ui_dict

    @cached_property
    def ui_offsets(self) -> dict:
        """
        回傳 UI 相關的偏移量與大小設定
        """
        return self.__config.get('ui_offsets', {})

    @cached_property
    def daily_prepare_images(self) -> dict:
        """
        讀取並回傳每日任務所需的圖片 (巢狀字典)
        """
        config = self.__config.get('daily_prepare', {})
        result = {}
        # config 結構為 Category -> Key -> Filename
        for category, items in config.items():
            result[category] = {}
            for key, filename in items.items():
                img_path = self.__photo_path / filename
                result[category][key] = PIL.Image.open(img_path)
        return result


if __name__ == "__main__":
    yaml_operator = YamlLoader()
    print(yaml_operator.boss_dict)
    print(yaml_operator.boss_dict)
    print(yaml_operator.skill_dict)
    print(yaml_operator.skill_dict)