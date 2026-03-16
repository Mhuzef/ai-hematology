from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Database
import uvicorn
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import base64
import os
from typing import Optional

app = FastAPI(title="AI Hematology Analyzer API")

# Setup CORS for the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO Model (Fallback to basic yolo11n.pt if trained one isn't found)
TRAINED_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "training", "runs", "detect", "yolov11_bccd", "weights", "best.pt")
try:
    if os.path.exists(TRAINED_WEIGHTS_PATH):
        print(f"Loading trained weights from: {TRAINED_WEIGHTS_PATH}")
        model = YOLO(TRAINED_WEIGHTS_PATH)
    else:
        print("Trained weights not found. Falling back to default yolo11n.pt.")
        model = YOLO('yolo11n.pt') 
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.on_event("startup")
async def startup_db_client():
    Database.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    Database.close()

@app.post("/analyze")
async def analyze_blood_slide(
    file: UploadFile = File(...),
    patient_name: Optional[str] = Form(None),
    blood_group: Optional[str] = Form(None),
    pt: Optional[str] = Form(None),
    bt: Optional[str] = Form(None),
    ct: Optional[str] = Form(None),
    hiv: Optional[str] = Form(None),
    hbsag: Optional[str] = Form(None),
    rbs: Optional[str] = Form(None),
    crp: Optional[str] = Form(None),
    ferritin: Optional[str] = Form(None),
    hba1c: Optional[str] = Form(None),
    esr: Optional[str] = Form(None),
):
    if model is None:
        raise HTTPException(status_code=500, detail="YOLO Model not loaded.")

    # 1. Read the image file correctly
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # 2. Run Inference
    results = model(image)[0]
    
    # 3. Use Supervision to parse results and annotate
    detections = sv.Detections.from_ultralytics(results)
    
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    
    labels = [
        f"{model.names[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    annotated_image = box_annotator.annotate(scene=image.copy(), detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

    # 4. Count the cells
    class_counts = {}
    for class_id in detections.class_id:
        class_name = model.names[class_id]
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    analysis = "Normal"
    if class_counts.get("RBC", 0) < 10:
         analysis = "Possible Anemia (Low RBC Count Detected)"
    elif class_counts.get("WBC", 0) > 5:
         analysis = "Possible Infection (High WBC Detected)"

    # 5. Encode annotated image back to base64
    _, buffer = cv2.imencode('.jpg', annotated_image)
    b64_image = base64.b64encode(buffer).decode('utf-8')

    # Construct the full lab data object
    lab_data = {
        "pt": pt, "bt": bt, "ct": ct,
        "hiv": hiv, "hbsag": hbsag,
        "rbs": rbs, "crp": crp, "ferritin": ferritin,
        "hba1c": hba1c, "esr": esr
    }

    report = {
        "filename": file.filename,
        "patient_name": patient_name,
        "blood_group": blood_group,
        "counts": class_counts,
        "lab_results": lab_data,
        "analysis": analysis,
        "annotated_image_base64": b64_image
    }

    # 6. Save to MongoDB (Optimistic: don't let DB failure block result)
    try:
        report_id = await Database.save_report({
            "filename": file.filename,
            "patient_name": patient_name,
            "blood_group": blood_group,
            "counts": class_counts,
            "lab_results": lab_data,
            "analysis": analysis
        })
        
        if report_id:
            report["id"] = report_id
        else:
             report["db_warning"] = "Analysis complete, but report was not saved to database."
    except Exception as e:
        print(f"Database save failed: {e}")
        report["db_warning"] = "Analysis complete, but database connection failed."

    return report

@app.get("/reports")
async def get_reports():
    return await Database.get_all_reports()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
