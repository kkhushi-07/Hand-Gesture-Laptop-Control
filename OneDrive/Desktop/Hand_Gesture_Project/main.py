import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import pyautogui
import math
# Pycaw ko sync karne ke liye wapas laya gaya hai
from pycaw.pycaw import AudioUtilities

# 1. Screen size settings setup
w_screen, h_screen = pyautogui.size()

# 2. Camera video configuration stream
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# 3. Hand Detector Setup
detector = HandDetector(maxHands=1, detectionCon=0.5)

# 4. Smooth motion variables
smooth_x, smooth_y = 0, 0
smoothing = 5

# 5. Windows Audio Sync Setup (Pycaw API integration)
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume  
vol_range = volume.GetVolumeRange()  
min_vol = vol_range[0]  # Minimum value (-65.25)
max_vol = vol_range[1]  # Maximum value (0.0)

# Initial local display values
vol_bar = 400
vol_per = 50

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)  # Mirror effect fix layout 
    hands, img = detector.findHands(img, draw=True)
    
    if hands:
        hand = hands[0]
        lm_list = hand["lmList"]  
        fingers = detector.fingersUp(hand)
        
        # Flags mapping status configuration
        index_open = fingers[1] == 1
        middle_open = fingers[2] == 1
        ring_open = fingers[3] == 1
        pinky_open = fingers[4] == 1
        
        # Euclidean distance calculate: Thumb tip (4) to Index tip (8)
        p1 = lm_list[4]
        p2 = lm_list[8]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        
        # Middle point tracking coordinates index
        cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2

        # ----------------------------------------------------
        # FEATURE 1: OPTION D - PINCH SLIDER VOLUME CONTROL (WITH SYNC)
        # ----------------------------------------------------
        if length < 35 and middle_open and ring_open and pinky_open:
            pinch_y = cy
            
            # 1. Pehle distance ko percentage (0-100) me convert karein
            vol_per = np.interp(pinch_y, (80, 400), (100, 0))
            vol_per = max(0, min(100, vol_per)) # Safe boundary check
            
            # 2. Percentage ke hisaab se visual blue status bar map karein
            vol_bar = np.interp(vol_per, (0, 100), (400, 150))
            
            # 3. CRITICAL SYNC FIX: Percentage ko direct Windows Volume Decibels par map karein
            target_db = np.interp(vol_per, (0, 100), [min_vol, max_vol])
            
            # 4. Windows Volume ko directly system hardware level par set karein
            volume.SetMasterVolumeLevel(target_db, None)

            # UI indicators feedback
            cv2.circle(img, (cx, cy), 15, (0, 128, 255), cv2.FILLED)
            cv2.putText(img, f'PINCH VOL: {int(vol_per)} %', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 128, 255), 2)
            
            cv2.rectangle(img, (30, 150), (60, 400), (0, 128, 255), 3)
            cv2.rectangle(img, (30, int(vol_bar)), (60, 400), (0, 255, 0), cv2.FILLED)

        # ----------------------------------------------------
        # FEATURE 2: MOUSE CURSOR (Sirf Index Finger Open)
        # ----------------------------------------------------
        elif index_open and not middle_open and not ring_open and not pinky_open:
            x1, y1 = lm_list[8][0], lm_list[8][1]
            
            x3 = np.interp(x1, (100, 540), (0, w_screen))
            y3 = np.interp(y1, (100, 380), (0, h_screen))
            
            smooth_x = smooth_x + (x3 - smooth_x) / smoothing
            smooth_y = smooth_y + (y3 - smooth_y) / smoothing
            
            pyautogui.moveTo(smooth_x, smooth_y)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            
        # ----------------------------------------------------
        # FEATURE 3: MOUSE LEFT CLICK (Index + Middle Open)
        # ----------------------------------------------------
        elif index_open and middle_open and not ring_open and not pinky_open:
            click_len, click_info, img = detector.findDistance(lm_list[8][:2], lm_list[12][:2], img)
            if click_len < 35:
                cv2.circle(img, (click_info[4], click_info[5]), 10, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                cv2.waitKey(200)  

    cv2.imshow("Hand Gesture Laptop Control", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
