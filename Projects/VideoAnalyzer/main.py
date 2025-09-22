from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from ultralytics import YOLO

app = FastAPI()

# Load the YOLOv8 model once on startup
model = YOLO("yolov8n.pt")  # 'n' = nano (smallest and fastest)

@app.get("/")
def read_root():
    return {"message": "Smart Surveillance API running with YOLOv8"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    try:
        # Read the uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Run inference with YOLOv8
        results = model.predict(frame, conf=0.4)

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])
            xyxy = list(map(int, box.xyxy[0].tolist()))  # [x1, y1, x2, y2]

            detections.append({
                "label": label,
                "confidence": round(conf, 2),
                "bbox": xyxy
            })

        return JSONResponse(content={"detections": detections})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
