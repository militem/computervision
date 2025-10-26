import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("yolov8n-seg.pt") 

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    for r in results:
        for seg, cls in zip(r.masks.data, r.boxes.cls):
            if int(cls) == 0:  
                seg = seg.cpu().numpy()
                mask = np.maximum(mask, (seg * 255).astype(np.uint8))

    blurred = cv2.GaussianBlur(frame, (55, 55), 0)

    mask_3 = cv2.merge([mask, mask, mask])
    output = np.where(mask_3 > 128, frame, blurred)

    cv2.imshow("Desenfoque de fondo", output)
    if cv2.waitKey(1) & 0xFF == 27: 
        break

cap.release()
cv2.destroyAllWindows()