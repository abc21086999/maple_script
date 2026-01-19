from pathlib import Path
import yaml

class SettingsManager:
    """
    負責管理 settings.yaml 的讀取與寫入。
    確保在寫入時不會覆蓋掉其他未更動的設定區塊。
    """
    def __init__(self, settings_path=None):
        if settings_path:
            self.settings_path = Path(settings_path)
        else:
            # 預設路徑：專案根目錄下的 config/settings.yaml
            self.settings_path = Path(__file__).resolve().parent.parent.parent / 'config' / 'settings.yaml'

        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """確保設定檔存在，如果不存在則建立一個空的"""
        if not self.settings_path.exists():
            # 確保資料夾存在
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump({}, f)

    def load_settings(self):
        """
        讀取整個設定檔
        :return: dict
        """
        if not self.settings_path.exists():
            return {}
        
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def get(self, section, key=None, default=None):
        """
        取得特定區塊或特定 key 的值
        :param section: 第一層的 key (例如 'daily_prepare')
        :param key: 第二層的 key (例如 'union_coin')，如果為 None 則回傳整個 section
        :param default: 如果找不到時的回傳值
        """
        data = self.load_settings()
        section_data = data.get(section, {})
        
        if key is None:
            return section_data
        
        return section_data.get(key, default)

    def save(self, section, data_to_update):
        """
        安全的儲存設定。
        先讀取最新檔案，合併更新該 section 的資料，再寫回。
        
        :param section: 要更新的區塊名稱 (str)
        :param data_to_update: 要更新的字典資料 (dict)
        """
        # 1. Load All (讀取現有檔案，避免覆蓋其他 section)
        full_data = self.load_settings()

        # 2. Merge (合併資料)
        if section not in full_data:
            full_data[section] = {}
        
        if isinstance(full_data[section], dict) and isinstance(data_to_update, dict):
            full_data[section].update(data_to_update)
        else:
            full_data[section] = data_to_update

        # 3. Dump All (寫回檔案)
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(full_data, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"Error saving settings: {e}")