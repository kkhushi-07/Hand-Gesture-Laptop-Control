# Hand Gesture Laptop Control 🚀

An AI-based computer vision project that allows users to control their laptop's mouse cursor, perform clicks, adjust system volume, and control screen brightness dynamically using real-time hand gestures.

## ✨ Features
- **Smooth Cursor Movement:** Uses Index Finger tracking with exponential smoothing to eliminate jitter.
- **Mouse Left Click:** Triggered seamlessly via an Index + Middle finger pinch gesture.
- **Synchronized Volume Control:** Uses a custom **Pinch Slider (Thumb + Index)** gesture mapped directly to Windows Master Audio via the Pycaw API.
- **Screen Brightness Engine:** Uses an isolated **Index + Pinky Finger Open** gesture to scale system brightness smoothly from 0% to 100%.

## 🛠️ Tech Stack
- Python 3.12
- OpenCV (cv2)
- Cvzone (MediaPipe wrapper)
- PyAutoGUI
- Pycaw (Windows Audio API)
- Screen-Brightness-Control (SBC API)

## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com
   cd YOUR_REPO_NAME
   ```
2. Activate your environment and install dependencies:
   ```bash
   pip install opencv-contrib-python cvzone pyautogui pycaw screen-brightness-control numpy
   ```
3. Run the project:
   ```bash
   python main.py
   ```
   *Press **`q`** on your keyboard while inside the webcam window to exit the application safely.*
