# Hand Gesture Laptop Control 🚀

An AI-based computer vision project that allows users to control their laptop's system functions, navigation, and core utilities dynamically using real-time hand gestures.

## ✨ Features
- **Smooth Cursor Movement:** Uses Index Finger tracking with exponential mathematical LERP smoothing to eliminate jitter.
- **Mouse Left Click:** Triggered seamlessly via an Index + Middle finger pinch gesture.
- **Right Click Trigger:** Activated when Index, Middle, and Ring finger tips touch each other closely.
- **Synchronized Volume Control:** Uses a custom **Pinch Slider (Thumb + Index)** gesture mapped directly to Windows Master Audio via the Pycaw API.
- **Screen Brightness Engine:** Uses an isolated **Index + Pinky Finger Open** gesture to scale system brightness smoothly from 0% to 100%.
- **Instant System Refresh:** Simply open your Pinky finger to send an immediate `F5` refresh call to your browser or desktop.
- **Clipboard Screenshot Engine:** Form a clean Fist (compress fingers) to capture a screenshot that instantly saves locally and injects straight into Windows memory for instant `Ctrl + V` pasting.

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
   cd Hand-Gesture-Laptop-Control
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