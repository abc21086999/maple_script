from pathlib import Path
import cv2
import numpy as np
from ai_edge_litert.compiled_model import CompiledModel
from ai_edge_litert.compiled_model import HardwareAccelerator


class RuneDetector:

    def __init__(self):
        self._model_dir_path = Path(__file__).parent.parent.parent / "models"
        self._model_path = self._model_dir_path / "model_unquant.tflite"
        self._labels_path = self._model_dir_path / "labels.txt"
        self._model = CompiledModel.from_file(str(self._model_path), HardwareAccelerator.GPU)
        self._LABELS = self._create_labels()
        self._create_buffer()

    def _create_buffer(self):
        """
        建立出入口的緩衝區
        """
        self._signature_index = 0
        self._input_buffers = self._model.create_input_buffers(self._signature_index)
        self._output_buffers = self._model.create_output_buffers(self._signature_index)

    def _create_labels(self):
        """
        讀取labels.txt
        """
        labels = []
        with open(self._labels_path, "r") as file:
            for line in file:
                direction = line.strip().split(" ")[-1]
                labels.append(direction)
        return labels

    @staticmethod
    def _image_processor(img):
        """
        處理影像
        """
        # 影像前處理
        if isinstance(img, str) or isinstance(img, Path):
            img = cv2.imread(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.expand_dims(img, 0)  # 變成 (1, 224, 224, 3)
        img = img.astype(np.float32)

        return img

    def predict(self, img):
        """
        利用模型去預測圖片
        """
        # 1. 拿到處理後的圖片
        process_img = self._image_processor(img)

        # 2. 將資料寫入「輸入緩衝區」
        self._input_buffers[0].write(process_img)

        # 3. 執行推論
        self._model.run_by_index(self._signature_index, self._input_buffers, self._output_buffers)

        # 4. 從「輸出緩衝區」讀取結果
        # 假設你的輸出是 4 個類別的機率，元素總數就是 4
        num_elements = 4
        output_array = self._output_buffers[0].read(num_elements, np.float32)

        # 取得預測結果
        class_idx = np.argmax(output_array)
        confidence = output_array[class_idx]

        return self._LABELS[class_idx], confidence


if __name__ == "__main__":
    detector = RuneDetector()
    img = cv2.imread("/Users/jasonhuang/Downloads/preview.png")
    print(f"原始圖片：dtype={img.dtype}, min={img.min()}, max={img.max()}")
    processed = RuneDetector._image_processor(img)
    print(f"處理後：dtype={processed.dtype}, min={processed.min():.3f}, max={processed.max():.3f}")

    label, confidence = detector.predict(img)
    print(f"辨識結果：{label}，信心度：{confidence:.2%}")