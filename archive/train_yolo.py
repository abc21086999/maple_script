from ultralytics import YOLO
import torch

def train_maple_model():
    """
    This script trains a YOLOv8 model on a custom dataset for MapleStory monsters.
    """
    # Check if a CUDA-enabled GPU is available and print the result
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Training on device: {device}")

    # Load a pre-trained YOLOv8 model.
    # 'yolov8n.pt' is the smallest and fastest model, good for starting.
    # You can also use 'yolov8s.pt', 'yolov8m.pt', etc., for better accuracy at the cost of speed.
    model = YOLO('yolov8n.pt')

    # --- Start Training ---
    # The `train` method takes several arguments to configure the training process.
    # data: Path to the .yaml file that describes the dataset.
    # epochs: The total number of training cycles. More epochs can lead to better performance but also overfitting.
    # imgsz: The image size for training. All images will be resized to this resolution.
    # batch: Number of images to process in a single batch. Adjust based on your GPU memory (-1 for auto-batch).
    # project: The directory where training results will be saved.
    # name: The specific name for this training run.
    try:
        results = model.train(
            data='maple_data.yaml', 
            epochs=100, 
            imgsz=640, 
            batch=-1, # Let ultralytics decide the best batch size
            project='runs/training',
            name='maple_monster_detector_v1'
        )
        print("Training completed successfully!")
        # The trained model and weights will be saved in 'runs/training/maple_monster_detector_v1/weights/'
        # The best performing model is saved as 'best.pt'.
        print(f"Trained model saved at: {results.save_dir}")

    except Exception as e:
        print(f"An error occurred during training: {e}")

if __name__ == '__main__':
    train_maple_model()
