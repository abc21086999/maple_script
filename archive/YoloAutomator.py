import time
import math
import dxcam
from ultralytics import YOLO
from src.XiaoController import XiaoController
from src.MapleScript import MapleScript


class YoloMapleAutomator(MapleScript):
    """
    一個使用 YOLO 模型進行物件偵測並自動化楓之谷操作的類別。
    繼承自 MapleScript，擴充了視覺辨識能力。
    """
    def __init__(self, controller: XiaoController, model_path: str):
        """
        初始化 Automator。

        :param controller: 一個已初始化的 XiaoController 物件。
        :param model_path: 訓練好的 YOLO 模型權重檔案 (.pt) 的路徑。
        """
        print("正在初始化YOLO自動化工具...")
        # 呼叫父類別 (MapleScript) 的初始化方法
        super().__init__(controller=controller)

        try:
            self.model = YOLO(model_path)
            print(f"模型 '{model_path}' 載入成功。")
            print("可辨識類別:", self.model.names)
        except Exception as e:
            print(f"錯誤：無法載入模型 '{model_path}'。請確認路徑是否正確。 {e}")
            raise

        try:
            # 從父類別 MapleScript 獲取 (left, top, width, height)
            left, top, width, height = self.maple_full_screen_area

            # 轉換成 (left, top, right, bottom) 格式給 DXCam 使用
            dxcam_region = (left, top, left + width, top + height)

            # 使用 MapleScript 取得的楓之谷視窗區域來初始化 DXCam，更精準
            self.camera = dxcam.create(region=dxcam_region)
            if not self.camera:
                raise ConnectionError("無法初始化 DXCam，請確認 DirectX 環境正常。")
            # 使用 DXCam 的區域來更新畫面中心點
            self.screen_width = self.camera.width
            self.screen_height = self.camera.height
            self.screen_center_x = self.screen_width // 2
            self.screen_center_y = self.screen_height // 2
            print(f"DXCam 畫面擷取器初始化成功，區域: {dxcam_region}")
        except Exception as e:
            print(f"錯誤：DXCam 初始化失敗。 {e}")
            raise

    def capture_and_detect(self) -> list:
        """
        擷取單一畫面並使用 YOLO 模型進行物件偵測。

        :return: YOLO 模型的偵測結果列表。
        """
        frame = self.camera.grab()
        if frame is None:
            # print("警告：無法擷取到畫面。") # 在快速循環中，此訊息可能過於頻繁
            return []

        results = self.model(frame, verbose=False)
        return results

    def find_closest_target(self, results: list, target_class_name: str, confidence_threshold: float = 0.6):
        """
        從偵測結果中找出最接近畫面中心的目標。

        :param results: YOLO 模型的偵測結果。
        :param target_class_name: 目標的類別名稱 (例如 'monster')。
        :param confidence_threshold: 信賴度閾值，低於此值將被忽略。
        :return: 一個包含目標資訊的字典 (box, class_name, center_x, center_y)，如果找不到則返回 None。
        """
        closest_target = None
        min_distance = float('inf')

        for result in results:
            for box in result.boxes:
                confidence = box.conf[0].cpu().numpy()
                if confidence < confidence_threshold:
                    continue

                class_id = int(box.cls[0].cpu().numpy())
                class_name = self.model.names[class_id]

                if class_name == target_class_name:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    distance = math.sqrt((center_x - self.screen_center_x)**2 + (center_y - self.screen_center_y)**2)

                    if distance < min_distance:
                        min_distance = distance
                        closest_target = {
                            "box": (x1, y1, x2, y2),
                            "class_name": class_name,
                            "center_x": center_x,
                            "center_y": center_y
                        }
        return closest_target

    def attack_target(self, target: dict, attack_key: str = 'a'):
        """
        使用 MapleScript 的方法來執行攻擊。

        :param target: 從 find_closest_target 返回的目標字典。
        :param attack_key: 用於攻擊的鍵盤按鍵。
        """
        if not target:
            return

        target_x, target_y = target['center_x'], target['center_y']
        print(f"偵測到最近的目標 {target['class_name']} 於 ({target_x}, {target_y})，開始攻擊。")

        # 使用繼承自 MapleScript 的 press_and_wait 方法
        self.press_and_wait(attack_key, wait_time=0.1)

    def run_grinding_loop(self, target_monster_name: str, attack_key: str = 'a', loop_delay: float = 0.5):
        """
        執行一個持續打怪的循環。

        :param target_monster_name: 要攻擊的怪物在模型中的類別名稱。
        :param attack_key: 攻擊按鍵。
        :param loop_delay: 每次循環之間的延遲（秒）。
        """
        print("啟動自動打怪循環... 按下 Ctrl+C 停止。")
        try:
            while True:
                if not self.is_maple_focus():
                    print("楓之谷不是前景視窗，暫停偵測。")
                    time.sleep(2)
                    continue

                results = self.capture_and_detect()
                monster = self.find_closest_target(results, target_monster_name)

                if monster:
                    self.attack_target(monster, attack_key=attack_key)
                else:
                    print("未偵測到怪物，執行尋找動作...")
                    self.press_and_wait('right', wait_time=0.5)

                time.sleep(loop_delay)

        except KeyboardInterrupt:
            print("\n自動化循環已停止。")
        finally:
            self.camera.stop()


if __name__ == '__main__':
    # --- 使用範例 ---
    # 請根據您的設定修改以下參數

    # 1. 指定您訓練好的模型路徑
    MODEL_PATH = 'runs/training/maple_monster_detector_v1/weights/best.pt'

    # 2. 指定您在 YOLO 標籤中為怪物設定的類別名稱
    TARGET_MONSTER_NAME = 'monster'  # 請改成您自己的類別名稱

    # 3. 指定您的主要攻擊技能按鍵
    ATTACK_KEY = 'q'

    # 採用與專案一致的寫法，使用 with 陳述式來管理 XiaoController
    try:
        with XiaoController() as controller:
            # 初始化自動化工具，並傳入 controller
            automator = YoloMapleAutomator(controller=controller, model_path=MODEL_PATH)

            # 啟動自動打怪循環
            automator.run_grinding_loop(
                target_monster_name=TARGET_MONSTER_NAME,
                attack_key=ATTACK_KEY
            )

    except Exception as e:
        print(f"程式執行時發生錯誤: {e}")
