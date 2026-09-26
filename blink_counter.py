import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector

cap = cv2.VideoCapture(0)


detector = FaceMeshDetector(maxFaces =1)

while True:

    # if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
    #     cap.set(cv2.CAP_PROP_FRAME_COUNT,0)  for video looping


    success, img = cap.read()
    img, faces  =detector.findFaceMesh(img)

    cv2.imshow("BLINK&SMILE",img)
    cv2.waitKey(1)
