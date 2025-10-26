import cv2
import numpy as np
from datetime import datetime

cap = cv2.VideoCapture("video1.avi")
fps = cap.get(cv2.CAP_PROP_FPS)

Bajo1 = np.array([0, 30, 60], np.uint8)
Alto1 = np.array([20, 150, 255], np.uint8)

Bajo2 = np.array([45, 5, 32], np.uint8)
Alto2 = np.array([50, 5, 51], np.uint8)

success, frame = cap.read()

while success and cv2.waitKey(1) == -1:
    success, frame = cap.read()
    code = datetime.now().strftime("%H%M%S")
    if success==True:
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(frameHSV, Bajo1, Alto1)
        mask2 = cv2.inRange(frameHSV, Bajo2, Alto2)
        mask = cv2.add(mask1, mask2)
        maskCompleted = cv2.bitwise_and(frame, frame, mask= mask)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f'cut_skin_{code}.png', maskCompleted)

cap.release()
cv2.destroyAllWindows()