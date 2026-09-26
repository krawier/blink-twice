import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector

cap = cv2.VideoCapture(0)


detector = FaceMeshDetector(maxFaces =1)

#based on these points on the face we can find the blinking

idList = [22,23,24,26,110,157,158,159,160,161,130,243]

while True:

    # if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
    #     cap.set(cv2.CAP_PROP_FRAME_COUNT,0)  for video looping


    success, img = cap.read()
    img, faces  =detector.findFaceMesh(img, draw = False)

    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img,face[id],4,(255,0,255), cv2.FILLED)

    cv2.imshow("BLINK&SMILE",img)
    cv2.waitKey(1)
