import cv2
import numpy as np
from datetime import datetime

def crear_mascaras(frame, rango1, rango2):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(frame_hsv, rango1[0], rango1[1])
    mask2 = cv2.inRange(frame_hsv, rango2[0], rango2[1])
    return cv2.add(mask1, mask2)


def procesar_video(path_video, ruta_video, rango1, rango2):
    cap = cv2.VideoCapture(f"{path_video}/{ruta_video}")
    if not cap.isOpened():
        print(f"No se pudo abrir el video: {ruta_video}")
        return

    ventana = f"Video - {ruta_video}"
    while True:
        success, frame = cap.read()
        if not success:
            break 
        mask = crear_mascaras(frame, rango1, rango2)
        mask_completed = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imshow(ventana, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('s'):
            code = datetime.now().strftime("%H%M%S")
            cv2.imwrite(f'results/cut_skin_{ruta_video}_{code}.png', mask_completed)
            print(f"Imagen guardada: cut_skin_{ruta_video}_{code}.png")
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cap.release()

def main():
    rango1 = (np.array([0, 30, 60], np.uint8), np.array([20, 150, 255], np.uint8))
    rango2 = (np.array([45, 5, 32], np.uint8), np.array([50, 5, 51], np.uint8))

    path_name = "assets"

    videos = ["video1.mp4", "video2.MOV", "video3.MOV"]

    for video in videos:
        procesar_video(path_name, video, rango1, rango2)

if __name__ == "__main__":
    main()
