import cv2
import copy
import threading
import os
import math
import numpy as np
from datetime import datetime

videoCapture = cv2.VideoCapture("assets/MyInputVideo.avi")
fps = videoCapture.get(cv2.CAP_PROP_FPS)

cv2.namedWindow("MyWindow")

size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
        int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

success, frame = videoCapture.read()
images_xy = []
lines = []
count_points = 0
vertices = []
square = [[0, 0], [1, 1], [2, 2], [3, 3]]

#Funciones

def distancia(punto):
    return math.sqrt(punto[0]**2 + punto[1]**2)

def save_frame(frame, square, code):
    puntos = [p for par in square for p in par]
    x_coords = [p[0] for p in puntos]
    y_coords = [p[1] for p in puntos]

    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    recorte = frame[y_min:y_max, x_min:x_max]
    cv2.imwrite(f'results/frame_recortado_{code}.jpg', recorte)
    print(f"Guardado completado: frame_recortado_{code}.jpg")

def validate_point(x, y, vertices):
    num_vertices = len(vertices)
    intersecciones = 0
    point = (x, y)

    for i in range(num_vertices):
        v1 = vertices[i]
        v2 = vertices[(i+1) % num_vertices]
        x1, y1 = v1
        x2, y2 = v2

        if((y1 <= point[1] < y2) or (y2 <= point[1] < y1)):
            if y1 != y2:
                x_interseccion = (point[1] - y1) * (x2 - x1) / (y2 - y1) + x1
            else:
                continue

            if point[0] < x_interseccion:
                intersecciones += 1
    
    return (intersecciones % 2) == 1

def cut_irregular_frame(frame, vertices):
    height, width =  frame.shape[:2]
    y_coords, x_coords = np.indices((height, width))
    test_points = np.stack((x_coords.ravel(), y_coords.ravel()), axis=-1)
    polygon = np.zeros(len(test_points), dtype=bool)

    print("Validando píxeles para recortar, puede tardar...")

    for i, (x, y) in enumerate(test_points):
        if validate_point(x, y, vertices):
            polygon[i] = True
    
    figure = polygon.reshape(height, width)
    background = np.zeros_like(frame)
    cut_figure = np.where(figure[..., np.newaxis], frame, background)

    return cut_figure

def worker_save_and_cut(frame_snapshot, vertices_snapshot, square_snapshot, code):
    try:
        save_frame(frame_snapshot, square_snapshot, code)

        figure_irregular = cut_irregular_frame(frame_snapshot, vertices_snapshot)
        cv2.imwrite(f'results/frame_cut_irregular_{code}.jpg', figure_irregular)
        cv2.imwrite(f'results/frame_with_lines_{code}.jpg', frame_snapshot)

        print(f"Guardado completado: frame_cut_irregular_{code}.jpg")
        print(f"Guardado completado: frame_with_lines_{code}.jpg")
    except Exception as e:
        print(f"Error durante guardado/recorte: {e}")

#Evento del mouse
def onMouse(event, x, y, flags, param):
    global frame
    global images_xy
    global lines
    global count_points
    global vertices

    if event == cv2.EVENT_LBUTTONDOWN:
        if count_points > 0:
            lines.append([images_xy[-1],[x,y]])
            vertices.append((x,y))

        if count_points >= 3:
            sorted_point = sorted(images_xy, key=distancia)
            up_left = sorted_point[-1]
            x1, y1 = up_left
            down_right = sorted_point[0]
            x2, y2 = down_right
            square[0] = [up_left, [x1, y2]]
            square[1] = [[x1, y2], down_right]
            square[2] = [down_right, [x2, y1]]
            square[3] = [[x2, y1], up_left]

        count_points += 1
        images_xy.append([x,y])

cv2.setMouseCallback('MyWindow', onMouse)

while success and cv2.waitKey(1) == -1:
    cv2.imshow('MyWindow', frame)
    code = datetime.now().strftime("%H%M%S")
    success, frame = videoCapture.read()
    for i in images_xy:
        cv2.circle(frame, center=(i[0], i[1]), radius=5, color=(0, 255, 0), thickness=2)
        try:    
            cv2.imshow("MyWindow", frame)
        except cv2.error:
            print("Cerrando programa...")

    for i in lines:
        cv2.line(frame, i[0], i[1], color=(255, 0, 0), thickness=2)
        try:    
            cv2.imshow("MyWindow", frame)
        except cv2.error:
            print("Cerrando programa...")

    if cv2.waitKey(25) & 0xFF == ord('s'):
        frame_copy = np.copy(frame)            
        vertices_copy = copy.deepcopy(vertices) 
        square_copy = copy.deepcopy(square) 
        code_for_thread = code

        t = threading.Thread(
            target=worker_save_and_cut,
            args=(frame_copy, vertices_copy, square_copy, code_for_thread),
            daemon=True
        )
        t.start()
        print("Imagenes guardadas...")
        try:    
            cv2.imshow("MyWindow", frame)
        except cv2.error:
            print("Cerrando programa...")

videoCapture.release()
cv2.destroyAllWindows()