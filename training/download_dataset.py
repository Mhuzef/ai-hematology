import os
from roboflow import Roboflow

def download_bccd_dataset():
    # Attempt to get the api key from the environment
    api_key = os.getenv("ROBOFLOW_API_KEY")
    if not api_key:
        print("ERROR: ROBOFLOW_API_KEY environment variable not found.")
        print("Please obtain an API key from Roboflow and run the script like this:")
        print("  Windows (PowerShell): $env:ROBOFLOW_API_KEY='your_api_key'; python download_dataset.py")
        print("  Linux/Mac: ROBOFLOW_API_KEY='your_api_key' python download_dataset.py")
        return None

    # We use a public BCCD dataset version available on Roboflow for YOLO training.
    # Note: Replace 'your-workspace' and 'project-name' if you are using your own annotation project!
    # For BCCD, standard public workspaces can be used:
    try:
        rf = Roboflow(api_key=api_key)
        # Using a public available workspace version of BCCD for YOLO
        # You may replace these parameters with a specific Roboflow public dataset link as needed.
        project = rf.workspace("blood-cell-count-dataset").project("bccd")
        version = project.version(1)
        dataset = version.download("yolov11") # yolov11 annotations are functionally similar to yolov8 natively
        print(f"Dataset downloaded successfully to: {dataset.location}")
        return dataset.location
    except Exception as e:
        print(f"Failed to download the dataset. Error: {e}")
        return None

if __name__ == "__main__":
    download_bccd_dataset()
