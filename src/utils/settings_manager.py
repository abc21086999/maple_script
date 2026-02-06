import json
import os
from pathlib import Path
import yaml
from PySide6.QtCore import QSettings, QStandardPaths


class SettingsManager:
    """
    分流儲存管理器：
    - 簡單的開關與設定存入 Windows Registry (QSettings)。
    - 複雜的結構 (如 grind_skills) 存入 AppData 中的 JSON 檔案。
    """

    # 定義哪些區塊應該儲存為檔案，以及它們在 AppData 內的檔案路徑
    # 格式為 { "區塊名稱": "子路徑" }
    STORAGE_ROUTING = {
        "grind_skills": "skills/skills.json",
        "toggle_skills": "toggle/toggle_skills.json",
        "recorded_route": "routes/recorded_route.json"
    }

    def __init__(self):
        # 取得 AppData/Local 路徑 (由 main.py 的 metadata 決定)
        self.base_data_path = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        
        # 初始化 QSettings (Registry)
        self.settings = QSettings()

        # 舊的設定檔路徑 (用於遷移)
        self.old_settings_path = Path(__file__).resolve().parent.parent.parent / 'config' / 'settings.yaml'

        # 執行遷移 (如果舊檔案存在)
        self._migrate_if_needed()

    def _get_file_path(self, section: str) -> Path:
        """根據映射表取得檔案的絕對路徑"""
        relative_path = self.STORAGE_ROUTING.get(section)
        if not relative_path:
            return None
        
        full_path = self.base_data_path / relative_path
        # 確保父資料夾存在
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    def get(self, section, key=None, default=None):
        """
        取得設定。自動判定從檔案讀取或從 Registry 讀取。
        """
        # 1. 判斷是否為檔案型資料
        file_path = self._get_file_path(section)
        if file_path:
            return self._load_from_file(file_path, key, default)
        
        # 2. 否則從 Registry 讀取
        return self._load_from_registry(section, key, default)

    def save(self, section, data_to_update):
        """
        儲存設定。自動判定寫入檔案或 Registry。
        """
        file_path = self._get_file_path(section)
        if file_path:
            self._save_to_file(file_path, data_to_update)
        else:
            self._save_to_registry(section, data_to_update)

    def _load_from_file(self, path: Path, key, default):
        """從 JSON 檔案讀取資料"""
        if not path.exists():
            return default if key else {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 路徑虛擬化：將 $APP_DATA$ 標記展開為當前電腦的真實絕對路徑
                data = self._process_paths(data, expand=True)
                
                if key is None:
                    return data
                return data.get(key, default)
        except Exception as e:
            print(f"Error loading JSON from {path}: {e}")
            return default if key else {}

    def _save_to_file(self, path: Path, data):
        """將資料寫入 JSON 檔案"""
        try:
            # 1. 讀取現有資料進行合併
            current_data = {}
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)

            if isinstance(current_data, dict) and isinstance(data, dict):
                current_data.update(data)
            else:
                current_data = data

            # 2. 路徑虛擬化：將絕對路徑收縮為 $APP_DATA$ 標記
            processed_data = self._process_paths(current_data, expand=False)

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON to {path}: {e}")

    def _process_paths(self, data, expand=True):
        """
        處理路徑的虛擬化 ($APP_DATA$ 標記)。
        採用遞迴處理，確保不論資料結構多深 (List/Dict) 都能處理到 image_path。
        """
        PREFIX = "$APP_DATA$"
        # 取得當前真實的 AppData 路徑字串，並統一使用正斜線
        real_app_data_path = str(self.base_data_path).replace('\\', '/')

        if isinstance(data, list):
            return [self._process_paths(item, expand) for item in data]
        
        elif isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                # 針對 image_path 欄位進行路徑處理
                if k == "image_path" and isinstance(v, str):
                    v_normalized = v.replace('\\', '/')
                    if expand:
                        # 展開：$APP_DATA$/skills/icon.png -> C:/Users/.../skills/icon.png
                        if v_normalized.startswith(PREFIX):
                            new_dict[k] = v_normalized.replace(PREFIX, real_app_data_path)
                        else:
                            new_dict[k] = v_normalized
                    else:
                        # 收縮：C:/Users/.../skills/icon.png -> $APP_DATA$/skills/icon.png
                        if v_normalized.startswith(real_app_data_path):
                            new_dict[k] = v_normalized.replace(real_app_data_path, PREFIX)
                        else:
                            new_dict[k] = v_normalized
                else:
                    # 遞迴處理子項目
                    new_dict[k] = self._process_paths(v, expand)
            return new_dict
        
        return data

    def _load_from_registry(self, section, key, default):
        """從 QSettings 讀取"""
        if key:
            val = self.settings.value(f"{section}/{key}", default)
            return self._convert_type(val)
        else:
            # 取得整個 section (群組)
            self.settings.beginGroup(section)
            data = {k: self._convert_type(self.settings.value(k)) for k in self.settings.childKeys()}
            self.settings.endGroup()
            return data if data else default

    def _save_to_registry(self, section, data):
        """將資料寫入 QSettings"""
        if not isinstance(data, dict):
            return

        self.settings.beginGroup(section)
        for k, v in data.items():
            self.settings.setValue(k, v)
        self.settings.endGroup()

    def _convert_type(self, val):
        """輔助函式：處理 QSettings 讀出的型別轉換問題 (特別是 bool)"""
        if isinstance(val, str):
            if val.lower() == 'true': return True
            if val.lower() == 'false': return False
            try:
                if '.' in val: return float(val)
                return int(val)
            except ValueError:
                return val
        return val

    def _migrate_if_needed(self):
        """一次性遷移：從 settings.yaml 搬移到新架構"""
        if not self.old_settings_path.exists():
            return

        print(f"偵測到舊設定檔，開始遷移至 AppData: {self.old_settings_path}")
        try:
            with open(self.old_settings_path, 'r', encoding='utf-8') as f:
                old_data = yaml.safe_load(f)
                if not old_data:
                    return

                for section, content in old_data.items():
                    self.save(section, content)
            
            # 遷移完成後重新命名舊檔案
            backup_path = self.old_settings_path.with_suffix('.yaml.bak')
            self.old_settings_path.rename(backup_path)
            print(f"遷移完成，舊檔案已更名為: {backup_path}")
        except Exception as e:
            print(f"遷移過程發生錯誤: {e}")
