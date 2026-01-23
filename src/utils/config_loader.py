import yaml
from pathlib import Path
import PIL.Image
from functools import cached_property


class YamlLoader:

    def __init__(self):
        self.__config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config.yaml"
        self.__grind_routes_path = Path(__file__).resolve().parent.parent.parent / "config" / "grind_routes.yaml"
        self.__recorded_route_path = Path(__file__).resolve().parent.parent.parent / "config" / "recorded_route.yaml"
        self.__photo_path = Path(__file__).resolve().parent.parent.parent / 'photos'
    
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
    def recorded_route(self):
        """
        讀取錄製好的練功路徑
        """
        if not self.__recorded_route_path.exists():
            return []
            
        with open(self.__recorded_route_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or []

    @cached_property
    def grind_setting(self):
        """
        提供練功相關的設定
        """
        return tuple(self.__config['grind_settings']['skill_gap_time'])

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
    def storage_resources(self) -> tuple[dict, dict]:
        """
        建立並回傳倉庫UI的號碼和圖片
        Returns:
            tuple[dict, dict]: (numbers_dict, ui_dict)
        """
        storage_config = self.__config["storage"]
        numbers_dict = {}
        ui_dict = {}

        # 處理數字圖片 (預設在 storage 資料夾下)
        for number, num_pic in storage_config.get('numbers', {}).items():
            img_path = self.__photo_path / "storage" / num_pic
            numbers_dict[number] = PIL.Image.open(img_path)

        # 處理 UI 圖片 (依照設定檔路徑)
        for name, pic_path in storage_config.get('ui', {}).items():
            img_path = self.__photo_path / pic_path
            ui_dict[name] = PIL.Image.open(img_path)

        return numbers_dict, ui_dict

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

    @cached_property
    def monster_collection_images(self) -> dict:
        """
        載入怪物收藏相關圖片
        """
        config = self.__config.get('monster_collection', {})
        images = {}
        for key, filename in config.items():
            img_path = self.__photo_path / filename
            images[key] = PIL.Image.open(img_path)
        return images

    @cached_property
    def menu(self) -> dict:
        """
        載入總攬界面當中的拍賣的圖片
        """
        config = self.__config.get('menu', {})
        images = {}
        for key, filename in config.items():
            img_path = self.__photo_path / filename
            images[key] = PIL.Image.open(img_path)
        return images

    @cached_property
    def daily_boss_images(self) -> dict:
        """
        載入每日Boss相關圖片
        """
        config = self.__config.get('daily_boss', {})
        result = {}
        # config 結構為 Category/Boss -> Key -> Filename
        for category, items in config.items():
            result[category] = {}
            for key, filename in items.items():
                img_path = self.__photo_path / "boss" / filename
                result[category][key] = PIL.Image.open(img_path)
        return result


if __name__ == "__main__":
    yaml_operator = YamlLoader()
    print(yaml_operator.user_grind_skills)
    print(yaml_operator.user_grind_skills)
    print(yaml_operator.user_grind_skills)
    print(yaml_operator.user_grind_skills)
