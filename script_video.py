import cv2
import math

videoCapture= cv2.VideoCapture(0)
fps= videoCapture.get(cv2.CAP_PROP_FPS)

cv2.namedWindow("MyWindow")

size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
        int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

videoWriter = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('I','4','2','0'), fps, size)

clicked = False

success, frame = videoCapture.read()
images_xy = []
lines = []
count_points = 0
square = [[0, 0], [1, 1], [2, 2], [3, 3]]

def distancia(punto):
    return math.sqrt(punto[0]**2 + punto[1]**2)

def save_frames(frame, square):
    puntos = [p for par in square for p in par]
    x_coords = [p[0] for p in puntos]
    y_coords = [p[1] for p in puntos]

    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    recorte = frame[y_min:y_max, x_min:x_max]
    cv2.imwrite('frame_recortado.jpg', recorte)


#Evento del mouse
def onMouse(event, x, y, flags, param):
    global clicked
    global frame
    global images_xy
    global lines
    global count_points

    if event == cv2.EVENT_LBUTTONDOWN:
        #clicked = True
        if count_points > 0:
            lines.append([images_xy[-1],[x,y]])

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
    # elif event == cv2.EVENT_RBUTTONUP:
        #clicked = True
    #    images_xy.pop()
    

while success and cv2.waitKey(1) == -1 and not clicked:
    cv2.imshow('MyWindow', frame)
    success, frame = videoCapture.read()
    for i in images_xy:
        #print(i[0], i[1])
        cv2.circle(frame, center=(i[0], i[1]), radius=5, color=(0, 255, 0), thickness=2)
        cv2.imshow("MyWindow", frame)

    for i in lines:
        #print(i[0], i[1])
        cv2.line(frame, i[0], i[1], color=(255, 0, 0), thickness=2)
        cv2.imshow("MyWindow", frame)

    cv2.setMouseCallback('MyWindow', onMouse)   

    if cv2.waitKey(25) & 0xFF == ord('q'):
        save_frames(frame, square)
        cv2.imwrite('frame_puntos.jpg', frame)
        

videoCapture.release()
cv2.destroyAllWindows()