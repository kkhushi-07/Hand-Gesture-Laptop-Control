import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import pyautogui
import math
import time
import os
import subprocess
from pycaw.pycaw import AudioUtilities
import screen_brightness_control as sbc

# CRITICAL FIX FOR PYAUTOGUI LAG
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Ensure Screenshots folder exists
if not os.path.exists("Screenshots"):
    os.makedirs("Screenshots")

w_screen, h_screen = pyautogui.size()

cap = cv2.VideoCapture(0)
cap.set(3, 640) 
cap.set(4, 480)

detector = HandDetector(maxHands=1, detectionCon=0.5)

smooth_x, smooth_y = 0, 0
lerp_weight = 0.25  

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume  
vol_range = volume.GetVolumeRange()  
min_vol = vol_range[0]
max_vol = vol_range[1]

# Screenshot trigger trackers
cooldown_timer = 0

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)  
    hands, img = detector.findHands(img, draw=True)
    
    if hands:
        hand = hands[0]
        lm_list = hand["lmList"]  
        fingers = detector.fingersUp(hand)
        
        index_open  = fingers[1] == 1
        middle_open = fingers[2] == 1
        ring_open   = fingers[3] == 1
        pinky_open  = fingers[4] == 1
        
        p_thumb = lm_list[4]
        p_index = lm_list[8]
        p_middle = lm_list[12]
        p_ring = lm_list[16]
        p_pinky = lm_list[20]
        
        # Exact Finger Tips to Base Spatial configurations
        # Used to strictly measure if a fist is compressed or flat
        index_tip_to_base = math.hypot(lm_list[8][0] - lm_list[5][0], lm_list[8][1] - lm_list[5][1])
        middle_tip_to_base = math.hypot(lm_list[12][0] - lm_list[9][0], lm_list[12][1] - lm_list[9][1])
        
        # ----------------------------------------------------
        # STABLE FIX: MATHEMATICAL FIST SCREENSHOT GENERATOR
        # GESTURE: Curl all fingers tight to make a Fist (Closed palm)
        # ----------------------------------------------------
        if index_tip_to_base < 35 and middle_tip_to_base < 35:
            if time.time() > cooldown_timer:
                ss_path = f"Screenshots/SS_{int(time.time())}.png"
                pyautogui.screenshot(ss_path)
                
                # Direct Native Windows Clipboard Injection (No pywin32 required)
                try:
                    abs_path = os.path.abspath(ss_path)
                    cmd = f"import-module pswindowsupdate; [Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{abs_path}'))"
                    subprocess.run(["powershell", "-command", f"Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{abs_path}'))"], shell=True)
                    print("Directly copied to Windows Memory Clipboard!")
                except Exception as e:
                    pass
                
                # Render visual prompt tracking confirmation
                cv2.putText(img, 'COPIED TO CLIPBOARD (CTRL+V)!', (60, 250), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Hand Gesture Laptop Control", img)
                cv2.waitKey(700)
                cooldown_timer = time.time() + 2.5 # Prevent multi-triggering cascades

        # 2. RIGHT CLICK (TOUCH GESTURE)
        elif index_open and middle_open and ring_open and not pinky_open:
            dist_1 = math.hypot(p_middle[0] - p_index[0], p_middle[1] - p_index[1])
            dist_2 = math.hypot(p_ring[0] - p_middle[0], p_ring[1] - p_middle[1])
            
            if dist_1 < 35 and dist_2 < 35:
                cv2.putText(img, 'RIGHT CLICK', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 0, 255), 2)
                pyautogui.rightClick()
                cv2.waitKey(400)

        # 3. REFRESH (F5)
        elif pinky_open and not index_open and not middle_open and not ring_open:
            cv2.putText(img, 'REFRESHING (F5)', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 0, 0), 2)
            pyautogui.press('f5')
            cv2.waitKey(400) 

        # 4. PINCH VOLUME CONTROL
        elif middle_open and ring_open and pinky_open:
            length = math.hypot(p_index[0] - p_thumb[0], p_index[1] - p_thumb[1])
            cx, cy = (p_thumb[0] + p_index[0]) // 2, (p_thumb[1] + p_index[1]) // 2
            
            if length < 35:
                pinch_y = cy
                vol_per = np.interp(pinch_y, (80, 400), (100, 0))
                vol_per = max(0, min(100, vol_per)) 
                target_db = np.interp(vol_per, (0, 100), [min_vol, max_vol])
                volume.SetMasterVolumeLevel(target_db, None)

                cv2.circle(img, (cx, cy), 15, (0, 128, 255), cv2.FILLED)
                cv2.putText(img, f'PINCH VOL: {int(vol_per)} %', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 128, 255), 2)

        # 5. BRIGHTNESS CONTROL
        elif index_open and pinky_open and not middle_open and not ring_open:
            b_length = math.hypot(p_pinky[0] - p_index[0], p_pinky[1] - p_index[1])
            bx, by = (p_index[0] + p_pinky[0]) // 2, (p_index[1] + p_pinky[1]) // 2
            
            bright_per = np.interp(b_length, (40, 180), (0, 100))
            bright_per = max(0, min(100, bright_per)) 
            sbc.set_brightness(int(bright_per))
            
            cv2.circle(img, (bx, by), 8, (0, 255, 255), cv2.FILLED)
            cv2.putText(img, f'BRIGHTNESS: {int(bright_per)} %', (50, 80), cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 0), 2)

        # 6. MOUSE CURSOR
        elif index_open and not middle_open and not ring_open and not pinky_open:
            x1, y1 = p_index[0], p_index[1]
            x3 = np.interp(x1, (100, 540), (0, w_screen))
            y3 = np.interp(y1, (100, 380), (0, h_screen))
            
            smooth_x = smooth_x + (x3 - smooth_x) * lerp_weight
            smooth_y = smooth_y + (y3 - smooth_y) * lerp_weight
            
            pyautogui.moveTo(int(smooth_x), int(smooth_y))
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            
        # 7. MOUSE LEFT CLICK
        elif index_open and middle_open and not ring_open and not pinky_open:
            click_len, click_info, img = detector.findDistance(p_index[:2], p_middle[:2], img)
            if click_len < 35:
                pyautogui.click()
                cv2.waitKey(200)  

    cv2.imshow("Hand Gesture Laptop Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

