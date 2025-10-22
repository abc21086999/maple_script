import yaml
from pathlib import Path
import PIL.Image


class YamlLoader:

    def __init__(self):
        self.__config_path = Path(__file__).resolve().parent / "config" / "config.yaml"
        self.__photo_path = Path(__file__).resolve().parent / 'photos'
        self.__config = None
        self.__load_yaml()
        self.skill_dict = self.__get_skills_dict()
        self.grind_setting = self.__get_grind_settings()

    def __load_yaml(self):
        """
        讀取YAML檔案
        :return: None
        """
        with open(self.__config_path, 'r', encoding='utf-8') as file:
            self.__config = yaml.safe_load(file)

    def __get_grind_settings(self):
        """
        提供練功相關的設定
        """
        return tuple(self.__config['grind_settings']['skill_gap_time'])

    def __get_skills_dict(self):
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


if __name__ == "__main__":
    yaml_operator = YamlLoader()
    for i in range(10):
        print(yaml_operator.skill_dict)