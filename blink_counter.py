import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
plotY = LivePlot(width, height, [20, 50], invert=True)

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
color = (255, 0, 255)

# --- Calibration Variables ---
calibrating = True
calibrationList = []
baselineRatio = 0
blinkThreshold = 0
openThreshold = 0

# --- Keyboard Variables ---
ratioList = []
framesClosed = 0
framesOpen = 0
quickBlinkCount = 0
currentWord = ""

while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 3, color, cv2.FILLED)

        # Distance calculations
        leftLefty = face[130]
        leftRight = face[243]
        leftUp1 = face[159]
        leftDown1 = face[23]
        leftUp2 = face[160]
        leftDown2 = face[24]

        horLen, _ = detector.findDistance(leftLefty, leftRight)
        vertLen1, _ = detector.findDistance(leftUp1, leftDown1)
        vertLen2, _ = detector.findDistance(leftUp2, leftDown2)

        vertLen = (vertLen1 + vertLen2) / 2
        ratio = int(((vertLen / horLen) * 100))

        # PHASE 1: AUTO-CALIBRATION ( ~3 Seconds)
        if calibrating:
            calibrationList.append(ratio)
            cvzone.putTextRect(img, "CALIBRATING... STARE AT CAMERA", (50, 100), colorR=(0, 0, 255))
            
            # After collecting 60 frames, calculate the user's specific baseline
            if len(calibrationList) >= 360:
                baselineRatio = sum(calibrationList) / len(calibrationList)
                
                # Set dynamic thresholds based on the baseline
                blinkThreshold = baselineRatio - 6  # Triggers when ratio drops 6 points below resting
                openThreshold = baselineRatio - 2   # Triggers when eyes return near resting
                calibrating = False
                
            imgPlot = plotY.update(ratio)

        # PHASE 2: ACTIVE TRACKING & TYPING
        else:
            ratioList.append(ratio)
            if len(ratioList) > 5:
                ratioList.pop(0)

            ratioAvg = sum(ratioList) / len(ratioList)

            # --- UPDATED LOGIC ---
            if ratioAvg < blinkThreshold:
                framesClosed += 1
                framesOpen = 0
                color = (0, 255, 0)
                
                # Delete the word IMMEDIATELY after holding for 40 frames
                if framesClosed == 40:
                    currentWord = ""
                    quickBlinkCount = 0
                    color = (0, 0, 255) # Turns RED to let you know it successfully deleted
                
            elif ratioAvg > openThreshold:
                color = (255, 0, 255)
                
                if framesClosed > 0:
                    # Only count as a quick blink if it was shorter than the 40-frame delete hold
                    if framesClosed < 40: 
                        quickBlinkCount += 1
                        
                    framesClosed = 0 
                    
                framesOpen += 1
                
                if framesOpen > 30 and quickBlinkCount > 0:
                    if quickBlinkCount == 1:
                        currentWord += " " 
                    elif quickBlinkCount >= 2:
                        letter = chr(63 + quickBlinkCount)
                        if letter.isalpha() and letter.isupper():
                            currentWord += letter
                            
                    quickBlinkCount = 0

            cvzone.putTextRect(img, f"Blinks: {quickBlinkCount}", (50, 50), scale=2, thickness=2, colorR=color)
            cvzone.putTextRect(img, f"Word: {currentWord}", (50, 120), scale=3, thickness=3, colorR=(0, 0, 0))
            cvzone.putTextRect(img, f"Base: {int(baselineRatio)} | Blink: {int(blinkThreshold)}", (50, height - 50), scale=2, colorR=(100, 100, 100))

            imgPlot = plotY.update(ratioAvg)

        imgStack = cvzone.stackImages([img, imgPlot], 2, 0.5) 
    else:
        imgStack = cvzone.stackImages([img, img], 2, 0.5)

    cv2.imshow("BLINK&SMILE", imgStack)
    cv2.waitKey(1)