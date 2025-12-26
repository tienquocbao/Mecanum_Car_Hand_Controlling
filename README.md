# 🏎️ AI Gesture Controlled Mecanum Car (ESP32 + MediaPipe)

[![Vietnamese](https://img.shields.io/badge/Lang-Vietnamese-red?style=for-the-badge)](README_vi.md)

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/Hardware-ESP32-red?logo=espressif&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-green?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange?logo=google&logoColor=white)

This project implements a real-time, hand-gesture-controlled robot car featuring Mecanum wheels for omnidirectional movement. It utilizes **Google MediaPipe** for hand tracking and **UDP communication** for low-latency control. The system features a futuristic Sci-Fi HUD with a split-screen interface for separate throttle and steering control.

## ✨ Key Features

* **Omnidirectional Movement:** Supports 8-direction movement (Forward, Backward, Crabs, Diagonals) and Spin turns.
* **Standalone WiFi (AP Mode):** The car acts as its own WiFi Hotspot, allowing operation anywhere without a router.
* **Split-Screen HUD Control:**
    * **Left Zone:** Throttle/Speed control via finger distance.
    * **Right Zone:** Joystick/Direction control via hand position vectors.
* **Smart Smoothing:** Implements a history buffer (counter-based filter) in Python to prevent jittery movements and ghost commands.
* **AI Vision:** Optimized for performance using MediaPipe Hands (Lite model logic).

### 🎥 Video Demo
[Demo Link](https://drive.google.com/file/d/1zi9xEzxrtOBP-PK36ziJwcpSPLFUbvFv/view?usp=sharing)

## 📂 Project Structure

* `control_new.py`: The main Python controller. It handles webcam input, hand gesture recognition, HUD rendering, smoothing logic, and sending UDP packets.
* `hand_controlling_mecanum_own_self_wifi.ino`: The C++ firmware for the ESP32. It creates the WiFi Access Point, parses UDP packets, and drives the motors.
* `environments.yaml`: The Conda environment configuration file ensuring all dependencies (OpenCV, MediaPipe, etc.) are installed correctly.

## 🛠️ Hardware Requirements

* **Microcontroller:** ESP32 Development Board.
* **Chassis:** 4-Wheel Mecanum Robot Chassis.
* **Motors:** 4x DC Motors.
* **Motor Driver:** L298N or equivalent (supporting 4 motors).
* **Power:** Li-ion Battery (2S or 3S recommended).
* **Host:** Laptop/PC with a Webcam.

### Pin Configuration (ESP32)
Based on the firmware:
* **Front Left (FL):** Pin 18, 19
* **Front Right (FR):** Pin 17, 5
* **Back Left (BL):** Pin 14, 12
* **Back Right (BR):** Pin 26, 27

## ⚙️ Installation & Setup

### 1. Python Environment (PC)
It is recommended to use **Conda** to avoid version conflicts.

```bash
# 1. Clone this repository
git clone https://github.com/tienquocbao/Mecanum_Car_Hand_Controlling.git
cd Mecanum_Car_Hand_Controlling

# 2. Create the environment from the yaml file
conda env create -f environments.yaml

# 3. Activate the environment (Name defined in yaml is 'robot_arm')
conda activate robot_arm
```

### 2. Firmware (ESP32)
1.  Open `hand_controlling_mecanum_own_self_wifi.ino` in Arduino IDE.
2.  Select **ESP32 Dev Module** as your board.
3.  Upload the code to your ESP32.

## 🚀 Usage Guide

### Step 1: Connect to the Car
Once powered on, the ESP32 will broadcast a WiFi signal:
* **SSID:** `wifi_name`
* **Password:** `password`

Connect your laptop to this WiFi network.

### Step 2: Run the Controller
Open your terminal (ensure `robot_arm` environment is active) and run:
```bash
python control_new.py
```
*The default target IP is `192.168.4.1` on Port `4212`.*

### Step 3: Driving Instructions (Gestures)

The camera view is split into two zones:

#### 🖐 LEFT ZONE (Throttle)
* Use your **Left Hand**.
* **Pinch (Thumb + Index):** Control speed.
    * **Far apart:** High Speed (Max 165).
    * **Close together:** Low Speed / Stop.

#### 🕹️ RIGHT ZONE (Steering)
Use your **Right Hand**. The gesture determines the "Mode", and the hand position determines the direction relative to the center.

| Gesture (Fingers Up) | Mode | Action |
| :--- | :--- | :--- |
| **5 Fingers (Open Hand)** | **STOP** | Emergency Stop. |
| **0 or 1 Finger (Fist)** | **ROTATE** | Move fist **Left** to Spin CCW, **Right** to Spin CW. |
| **3 Fingers (Thumb, Index, Middle)** | **LINEAR** | Move hand Up, Down, Left, or Right to drive normally. |
| **3 Fingers (Middle, Ring, Pinky)** | **DIAGONAL** | Move hand to corners to drift diagonally (FL, FR, BL, BR). |

## 👨‍💻 Author
**Student:** [Tien Quoc Bao]
**University:** FPT University Can Tho
**Major:** Artificial Intelligence (AI)#


