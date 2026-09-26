import cv2
import cvzone

cap = cv2.VideoCapture(0)


while True:
    success, img = cap.read()
    cv2.imshow("BLINK&SMILE",img)
    cv2.waitKey(1)