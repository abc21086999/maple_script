from pathlib import Path

target_dir = Path(r"C:\Users\abc21\Pictures\image_for_test")

for i, img_path in enumerate(sorted(target_dir.glob("*.png"))):
    img_path.rename(target_dir / f"{i}.png")
    print(f"已重新命名：{img_path.name} → {i}.png")

print("完成！")