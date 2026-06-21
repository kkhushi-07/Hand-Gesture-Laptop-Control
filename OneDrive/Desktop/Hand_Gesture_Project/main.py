import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import pyautogui
import math
# Pycaw audio module sync setup
from pycaw.pycaw import AudioUtilities
# Screen brightness optimization framework
import screen_brightness_control as sbc

# 1. Screen size settings setup
w_screen, h_screen = pyautogui.size()

# 2. Camera video configuration stream (Default Webcam)
cap = cv2.VideoCapture(0)
cap.set(3, 640) 
cap.set(4, 480)

# 3. Hand Detector Setup (Strictly 1 Hand to save system memory)
detector = HandDetector(maxHands=1, detectionCon=0.5)

# 4. Smooth motion variables for mouse cursor navigation
smooth_x, smooth_y = 0, 0
smoothing = 5

# 5. Windows Audio Sync Setup (Pycaw API integration)
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume  
vol_range = volume.GetVolumeRange()  
min_vol = vol_range[0]  # Minimum hardware value (-65.25)
max_vol = vol_range[1]  # Maximum hardware value (0.0)

# Initial local display calibration status constants
vol_bar = 400
vol_per = 50
bright_per = 50  # Initial placeholder balance metric

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)  # Lateral Inversion / Mirror effect fix layout 
    hands, img = detector.findHands(img, draw=True)
    
    if hands:
        hand = hands[0]
        lm_list = hand["lmList"]  
        fingers = detector.fingersUp(hand)
        
        # Binary flags tracking for individual finger arrays
        thumb_open  = fingers[0] == 1
        index_open  = fingers[1] == 1
        middle_open = fingers[2] == 1
        ring_open   = fingers[3] == 1
        pinky_open  = fingers[4] == 1
        
        # Euclidean distance calculations: Thumb tip (4) to Index tip (8) [For Volume Slider Only]
        p1 = lm_list[4]
        p2 = lm_list[8]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        
        # Center tracking point matrix for visual calibration tracking
        cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2

        # ----------------------------------------------------
        # FEATURE 1: PINCH SLIDER VOLUME CONTROL (WITH PYCAW SYNC)
        # GESTURE: Thumb + Index Pinch (Middle, Ring, Pinky must be OPEN)
        # ----------------------------------------------------
        if length < 35 and middle_open and ring_open and pinky_open:
            pinch_y = cy
            
            # Distance mapping array logic scales vertical pixel workspace cleanly
            vol_per = np.interp(pinch_y, (80, 400), (100, 0))
            vol_per = max(0, min(100, vol_per)) # Hardware safety bounds check
            
            vol_bar = np.interp(vol_per, (0, 100), (400, 150))
            
            # Converts percentage metric to system decibels smoothly
            target_db = np.interp(vol_per, (0, 100), [min_vol, max_vol])
            volume.SetMasterVolumeLevel(target_db, None)

            # Graphical UI adjustments for terminal display tracking
            cv2.circle(img, (cx, cy), 15, (0, 128, 255), cv2.FILLED)
            cv2.putText(img, f'PINCH VOL: {int(vol_per)} %', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 128, 255), 2)
            
            cv2.rectangle(img, (30, 150), (60, 400), (0, 128, 255), 3)
            cv2.rectangle(img, (30, int(vol_bar)), (60, 400), (0, 255, 0), cv2.FILLED)

        # ----------------------------------------------------
        # FEATURE 4: BRIGHTNESS CONTROL ENGINE (NEW ISOLATED FEATURE)
        # GESTURE: Index + Pinky OPEN (Thumb, Middle, Ring must be CLOSED)
        # ----------------------------------------------------
        elif index_open and pinky_open and not middle_open and not ring_open and not thumb_open:
            # Isolating Index tip (8) and Pinky tip (20) spatial configurations
            p_index = lm_list[8]
            p_pinky = lm_list[20]
            
            # Accurate distance matrix formulation
            b_length = math.hypot(p_pinky[0] - p_index[0], p_pinky[1] - p_index[1])
            bx, by = (p_index[0] + p_pinky[0]) // 2, (p_index[1] + p_pinky[1]) // 2
            
            # Direct mapping range setup (Dynamic distance scale thresholds 40 to 180 pixels)
            bright_per = np.interp(b_length, (40, 180), (0, 100))
            bright_per = max(0, min(100, bright_per)) # Boundary guard
            
            # Overrides native operating system brightness registers smoothly
            sbc.set_brightness(int(bright_per))
            
            # Visual design elements render engine
            cv2.circle(img, (p_index[0], p_index[1]), 10, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, (p_pinky[0], p_pinky[1]), 10, (255, 255, 0), cv2.FILLED)
            cv2.line(img, (p_index[0], p_index[1]), (p_pinky[0], p_pinky[1]), (255, 255, 0), 3)
            cv2.circle(img, (bx, by), 8, (0, 255, 255), cv2.FILLED)
            cv2.putText(img, f'BRIGHTNESS: {int(bright_per)} %', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 0), 2)

        # ----------------------------------------------------
        # FEATURE 2: MOUSE CURSOR TRACKING MANAGEMENT
        # GESTURE: Only Index Finger OPEN (All other fingers must be CLOSED)
        # ----------------------------------------------------
        elif index_open and not middle_open and not ring_open and not pinky_open:
            x1, y1 = lm_list[8][0], lm_list[8][1]
            
            # Map camera capture coordinate limits to native user viewport pixel resolutions
            x3 = np.interp(x1, (100, 540), (0, w_screen))
            y3 = np.interp(y1, (100, 380), (0, h_screen))
            
            # Exponential moving filter smoothing architecture
            smooth_x = smooth_x + (x3 - smooth_x) / smoothing
            smooth_y = smooth_y + (y3 - smooth_y) / smoothing
            
            pyautogui.moveTo(smooth_x, smooth_y)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            
        # ----------------------------------------------------
        # FEATURE 3: MOUSE LEFT CLICK TRIGGER
        # GESTURE: Index + Middle OPEN (Thumb, Ring, Pinky must be CLOSED)
        # ----------------------------------------------------
        elif index_open and middle_open and not ring_open and not pinky_open:
            click_len, click_info, img = detector.findDistance(lm_list[8][:2], lm_list[12][:2], img)
            if click_len < 35:
                cv2.circle(img, (click_info[4], click_info[5]), 10, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                cv2.waitKey(200)  # Mechanical bounce filter delay simulation 

    cv2.imshow("Hand Gesture Laptop Control", img)
    
    # Secure escape sequence break protocol
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
