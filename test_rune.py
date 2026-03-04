import cv2
import numpy as np
import tensorflow as tf

# 載入模型
interpreter = tf.lite.Interpreter(model_path="models/model_unquant.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

LABELS = ["up", "down", "right", "left"]  # 順序要跟 labels.txt 一致！


def predict(img):
    # 縮放成模型期望的大小
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, 0)  # 加 batch 維度

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])
    class_idx = np.argmax(output)
    confidence = output[0][class_idx]

    return LABELS[class_idx], confidence


# 測試一張圖
img = cv2.imread(r"C:\Users\abc21\Pictures\Screenshots\t.png")  # 放一張你的箭頭截圖
label, confidence = predict(img)
print(f"辨識結果：{label}，信心度：{confidence:.2%}")