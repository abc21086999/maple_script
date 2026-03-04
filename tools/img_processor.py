from pathlib import Path
import cv2

input_dir = Path(r"C:\Users\abc21\Pictures\image_for_test")
output_dir = Path(r"C:\Users\abc21\Pictures\image_for_test")
output_dir.mkdir(exist_ok=True)

# 上下各裁掉幾個百分比（你可以調整這個數字）
CROP_TOP = 0.15  # 裁掉上面 10%
CROP_BOTTOM = 0.15  # 裁掉下面 10%

# 每個箭頭小圖的左右裁切
ARROW_CROP_LEFT = 0.15
ARROW_CROP_RIGHT = 0.15

for img_path in input_dir.glob("*.png"):
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]

    # 先裁掉整張圖的上下
    top = int(h * CROP_TOP)
    bottom = int(h * (1 - CROP_BOTTOM))
    img = img[top:bottom, :]

    # 切成四等份，每份再裁左右
    arrow_w = w // 4
    for i in range(4):
        arrow = img[:, i * arrow_w:(i + 1) * arrow_w]

        # 對每個箭頭小圖再裁左右
        aw = arrow.shape[1]
        left = int(aw * ARROW_CROP_LEFT)
        right = int(aw * (1 - ARROW_CROP_RIGHT))

        if i == 0:
            left += int(aw * 0.2)
        if i == 1:
            left += int(aw * 0.15)  # 第二個左邊少裁一點
        if i == 2:
            right -= int(aw * 0.15)  # 第三個右邊少裁一點
        if i == 3:
            right -= int(aw * 0.2)

        arrow = arrow[:, left:right]

        output_path = output_dir / f"{img_path.stem}_{i}.png"
        cv2.imwrite(str(output_path), arrow)
        print(f"已儲存：{output_path}")

print("完成！")