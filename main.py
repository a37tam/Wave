import cv2
import numpy as np
import pyautogui as pag
import math


def getVector(pt1, pt2):
    return [pt1[0] - pt2[0], pt1[1] - pt2[1]]


def getDistance(v):
    return math.sqrt(pow(v[0], 2) + (pow(v[1], 2)))


def getAngle(pt1, pt2, pt3):
    v1 = getVector(pt1, pt3)
    v2 = getVector(pt2, pt3)
    x = v1[0] * v2[0] + v1[1] * v2[1]
    y = getDistance(v1) * getDistance(v2)
    return math.degrees(math.acos(x / y))


pag.FAILSAFE = False
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
SCREEN_WIDTH, SCREEN_HEIGHT = pag.size()
FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
FRAME_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
SCALE_X = SCREEN_WIDTH / FRAME_WIDTH
SCALE_Y = SCREEN_HEIGHT / FRAME_HEIGHT


while (cap.isOpened()):
    ret1, frame = cap.read()
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (30, 30))
    ret2, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)

    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

    hull = cv2.convexHull(contour, returnPoints=True)
    cv2.drawContours(frame, [hull], -1, (0, 0, 255), 2)

    hullIndices = cv2.convexHull(contour, clockwise=False, returnPoints=False)
    convexityDefects = cv2.convexityDefects(contour, hullIndices)
    relevantDefects = []

    for i in range(0, len(convexityDefects)):
        s, e, f, d = convexityDefects[i, 0]
        pt1 = (contour[s])[0]
        pt2 = (contour[e])[0]
        pt3 = (contour[f])[0]
        if getAngle(pt1, pt2, pt3) < 90:
            if relevantDefects == [] or getDistance(getVector(relevantDefects[-1], pt1)) > 20:
                relevantDefects.append(pt1)
            relevantDefects.append(pt2)

    for i in range(0, len(relevantDefects)):
        cv2.circle(frame, tuple(relevantDefects[i]), 5, (255, 255, 255), 3)

    numberOfDefects = len(relevantDefects)

    if numberOfDefects == 2:
        x = (relevantDefects[0][0]) * SCALE_X
        y = (relevantDefects[0][1]) * SCALE_Y
        pag.moveTo(x, y, duration=0.1)
    elif numberOfDefects == 3:
        pag.click(button='left')
    elif numberOfDefects == 4:
        pag.click(button='right')
    else:
        pass

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
cap.release()
