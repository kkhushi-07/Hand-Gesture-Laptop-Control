# Hand Gesture Laptop Control 🚀

An AI-based computer vision project that allows users to control their laptop's mouse cursor, perform clicks, and adjust system volume dynamically using real-time hand gestures.

## ✨ Features
- **Smooth Cursor Movement:** Uses Index Finger tracking with exponential smoothing.
- **Mouse Left Click:** Triggered via Index + Middle finger pinch.
- **Synchronized Volume Control:** Uses a custom **Pinch Slider (Thumb + Index)** gesture mapped directly to Windows Master Audio.

## 🛠️ Tech Stack
- Python 3.12
- OpenCV
- Cvzone (MediaPipe wrapper)
- PyAutoGUI

## 🚀 How to Run
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the project: `python main.py`
