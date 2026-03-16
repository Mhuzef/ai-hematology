import os
from ultralytics import YOLO

def train_hematology_model(data_yaml_path: str, epochs: int = 50, imgsz: int = 640):
    """
    Fine-tunes YOLOv11 on the provided Blood Cell count dataset.
    
    Args:
    data_yaml_path (str): The path to the data.yaml file inside the downloaded dataset.
    epochs (int): Number of epochs to train for.
    imgsz (int): Image size to train at.
    """
    if not os.path.exists(data_yaml_path):
        print(f"ERROR: Dataset not found at {data_yaml_path}")
        print("Please download the dataset first using 'download_dataset.py'.")
        return

    print("Loading YOLOv11 weights...")
    # Load the base YOLOv11 model (n = nano, s = small, m = medium)
    # n is chosen for quick prototype/web-deployment inference speed.
    model = YOLO('yolo11n.pt') 

    print(f"Starting training on {data_yaml_path} for {epochs} epochs...")
    # Train the model
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=16,          # Adjust depending on your GPU memory
        name='yolov11_bccd', # Folder name inside 'runs/detect' saving the results
        device='0' if os.environ.get("CUDA_VISIBLE_DEVICES") else 'cpu' # Using GPU if available
    )

    print("Training Complete!")
    print("The best weights will be saved in 'runs/detect/yolov11_bccd/weights/best.pt'")
    
    # Exporting the model as part of the phase!
    export_path = model.export(format="onnx")
    print(f"Model also exported to ONNX format at {export_path}")

if __name__ == "__main__":
    # Update this path based on where the Roboflow script downloaded the dataset
    # E.g., if it downloaded to "BCCD-1", then it's "BCCD-1/data.yaml"
    DATASET_YAML = os.path.join("BCCD-1", "data.yaml")
    
    # Alternatively accept path as argument
    import sys
    if len(sys.argv) > 1:
        DATASET_YAML = sys.argv[1]
        
    train_hematology_model(DATASET_YAML)
