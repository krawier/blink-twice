import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import requests
import threading
import pyttsx3
import numpy as np

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
plotY = LivePlot(width, height, [20, 50], invert=True)

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
color = (255, 0, 255)

# --- Dictionary & State Variables ---
medical_dictionary = [
    # --- Nagłe ---
    "BÓL", "DUSZNO", "PANIKA", "POMOC", "SSAK",
    "PIELĘGNIARKA", "LEKARZ", "LEKI", "KROPLÓWKA",
    
    # --- Potrzeby fizjologiczne ---
    "WODA", "JEDZENIE", "TOALETA", "MOKRO", "ZIMNO", "GORĄCO", 
    
    # --- Komfort  ---
    "PODUSZKA", "KOC", "SIEDZIEĆ", "LEŻEĆ", "OBRÓCIĆ", 
    "NIEWYGODNIE", "SWĘDZI", "SKURCZ",
    
    # --- Otoczenie (Environment) ---
    "ŚWIATŁO", "CICHY", "GŁOŚNO", "ZAMKNIJ", "OTWÓRZ", 
    
    # --- Komunikacja / Prywatne ---
    "TAK", "NIE", "DZIĘKUJĘ", "TELEFON", "OKULARY", "RODZINA"
]

available_words = medical_dictionary.copy()
current_prefix = ""

system_state = "IDLE"  
current_letter_index = 0
possible_next_letters = []

# --- Timing Variables ---
calibrating = True
calibrationList = []
baselineRatio = 0
blinkThreshold = 0
openThreshold = 0

ratioList = []
framesClosed = 0
framesDwell = 0  
DWELL_LIMIT = 60 

def get_possible_letters(prefix, words):
    letters = set()
    for w in words:
        if len(w) > len(prefix):
            letters.add(w[len(prefix)])
    return sorted(list(letters))

def speak_async(text):
    def run_tts():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'Polish' in voice.name or 'PL' in voice.id:
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
        
    threading.Thread(target=run_tts, daemon=True).start()

while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)
    
    # Create a blank black canvas for the UI panel
    imgUI = np.zeros((height, width, 3), np.uint8)

    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 3, color, cv2.FILLED)

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

        # ==========================================
        # PHASE 1: AUTO-CALIBRATION
        # ==========================================
        if calibrating:
            calibrationList.append(ratio)
            cvzone.putTextRect(imgUI, "STARE AT CAMERA", (50, 100), colorR=(0, 0, 255))
            
            if len(calibrationList) >= 360:
                baselineRatio = sum(calibrationList) / len(calibrationList)
                blinkThreshold = baselineRatio - 6  
                openThreshold = baselineRatio - 2   
                calibrating = False
                
            imgPlot = plotY.update(ratio)

        # ==========================================
        # PHASE 2: DWELL TIME STATE MACHINE
        # ==========================================
        else:
            ratioList.append(ratio)
            if len(ratioList) > 5:
                ratioList.pop(0)

            ratioAvg = sum(ratioList) / len(ratioList)

            if ratioAvg < blinkThreshold:
                framesClosed += 1
                framesDwell = 0 
                color = (0, 255, 0)
            else:
                color = (255, 0, 255)
                
                if framesClosed > 0:
                    if system_state == "IDLE":
                        if framesClosed >= 75: 
                            system_state = "SCANNING"
                            current_prefix = ""
                            available_words = medical_dictionary.copy()
                            possible_next_letters = get_possible_letters(current_prefix, available_words)
                            current_letter_index = 0
                            speak_async(possible_next_letters[0]) 
                            
                    elif system_state == "SCANNING":
                        if 3 <= framesClosed < 30: 
                            current_letter_index += 1
                            if current_letter_index >= len(possible_next_letters):
                                current_letter_index = 0
                            speak_async(possible_next_letters[current_letter_index])
                            
                        elif framesClosed >= 60: 
                            system_state = "IDLE"
                            current_prefix = ""
                            speak_async("Anulowano") 

                    framesClosed = 0 
                
                if system_state == "SCANNING":
                    framesDwell += 1
                    
                    if framesDwell >= DWELL_LIMIT:
                        selected_letter = possible_next_letters[current_letter_index]
                        current_prefix += selected_letter
                        speak_async("Wybrano")
                        
                        available_words = [w for w in available_words if w.startswith(current_prefix)]
                        
                        if len(available_words) == 1 and available_words[0] == current_prefix:
                            cvzone.putTextRect(imgUI, "SENDING...", (width//2 - 100, height//2), scale=3, colorR=(0, 200, 0))
                            cv2.imshow("BLINK&SMILE", img) # Temporarily show just the camera
                            cv2.waitKey(500)
                            
                            print(f"--- SENT TO DASHBOARD: {current_prefix} ---")
                            speak_async("Wysłano komunikat")
                            
                            system_state = "IDLE"
                            current_prefix = ""
                            available_words = medical_dictionary.copy()
                        else:
                            possible_next_letters = get_possible_letters(current_prefix, available_words)
                            current_letter_index = 0
                            speak_async(possible_next_letters[0])
                            
                        framesDwell = 0 

            # ==========================================
            # UI VISUALS (Now drawn on imgUI instead of img)
            # ==========================================
            cvzone.putTextRect(imgUI, f"State: {system_state}", (50, 50), scale=2, thickness=2, colorR=color)
            
            if system_state == "SCANNING":
                cvzone.putTextRect(imgUI, f"Prefix: {current_prefix}", (50, 120), scale=2, colorR=(0, 0, 0))
                
                if possible_next_letters:
                    cvzone.putTextRect(imgUI, f"Letter: {possible_next_letters[current_letter_index]}", (50, 200), scale=4, thickness=4, colorR=(200, 0, 0))
                    
                    next_idx = (current_letter_index + 1) % len(possible_next_letters)
                    if len(possible_next_letters) > 1:
                        cvzone.putTextRect(imgUI, f"Next -> {possible_next_letters[next_idx]}", (50, 310), scale=2, colorR=(150, 150, 150))
                    
                    bar_width = int((framesDwell / DWELL_LIMIT) * 200)
                    cv2.rectangle(imgUI, (50, 250), (50 + bar_width, 270), (0, 255, 0), cv2.FILLED)
                    cv2.rectangle(imgUI, (50, 250), (250, 270), (255, 255, 255), 2) 
            
            cvzone.putTextRect(imgUI, f"Matches: {len(available_words)}", (50, height - 50), scale=2, colorR=(100, 100, 100))
            imgPlot = plotY.update(ratioAvg)

        # Stack into 3 columns: Camera, UI Canvas, Graph
        imgStack = cvzone.stackImages([img, imgUI, imgPlot], 3, 0.7) 
    else:
        # Maintain layout even if face tracking drops
        imgStack = cvzone.stackImages([img, imgUI, img], 3, 0.7)

    cv2.imshow("BLINK&SMILE", imgStack)
    cv2.waitKey(1)