import json
import os
from pathlib import Path
from PySide6.QtCore import QStandardPaths


class SettingsManager:
    """
    分流儲存管理器：
    - 所有設定均存入 AppData 中的 JSON 檔案。
    - 支援路徑虛擬化 ($APP_DATA$) 以確保跨裝置相容性。
    """

    # 定義哪些區塊應該儲存為檔案，以及它們在 AppData 內的檔案路徑
    # 格式為 { "區塊名稱": "子路徑" }
    STORAGE_ROUTING = {
        "grind_skills": "skills/skills.json",
        "toggle_skills": "toggle/toggle_skills.json",
        "recorded_route": "routes/recorded_route.json",
        "daily_prepare": "tasks/daily_prepare.json",
        "grind_settings": "tasks/grind_settings.json",
        "hardware": "system/hardware.json"
    }

    def __init__(self):
        # 取得 AppData/Local 路徑 (由 main.py 的 metadata 決定)
        self.base_data_path = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))

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
        取得設定。僅支援已定義在 STORAGE_ROUTING 中的項目。
        """
        file_path = self._get_file_path(section)
        
        if not file_path:
            return default if key is not None else {}
            
        return self._load_from_file(file_path, key, default)

    def save(self, section, data_to_update, file_name=None):
        """
        儲存設定。僅支援已定義在 STORAGE_ROUTING 中的項目，或明確指定 file_name。
        """
        file_path = None
        
        if file_name:
            file_path = self.base_data_path / file_name
        else:
            file_path = self._get_file_path(section)
        
        if not file_path:
             print(f"Error: Cannot save to undefined section '{section}' without a file_name.")
             return

        # 確保父資料夾存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self._save_to_file(file_path, data_to_update)

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