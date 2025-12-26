# 🏎️ AI Gesture Controlled Mecanum Car (ESP32 + MediaPipe)

[![English](https://img.shields.io/badge/Lang-English-blue?style=for-the-badge)](README.md)

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/Hardware-ESP32-red?logo=espressif&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-green?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange?logo=google&logoColor=white)

Dự án điều khiển xe Mecanum đa hướng bằng cử chỉ tay (Hand Gestures) thông qua Camera máy tính. Hệ thống sử dụng **Python (MediaPipe)** để xử lý hình ảnh và gửi lệnh điều khiển qua giao thức **UDP** đến **ESP32** với độ trễ cực thấp.

Giao diện điều khiển (HUD) được thiết kế theo phong cách Sci-Fi với cơ chế chia đôi màn hình (Split-screen) giúp điều khiển chính xác.

## ✨ Tính năng nổi bật

* **Omnidirectional Movement:** Di chuyển 8 hướng (Tiến, Lùi, Trái, Phải và 4 hướng chéo) + Xoay vòng tại chỗ.
* **Standalone WiFi (AP Mode):** Xe tự phát Wifi, không cần Router trung gian, chơi được ở bất cứ đâu.
* **Split-Screen Control:**
    * 🖐 **Tay Trái:** Điều khiển tốc độ (Throttle) dựa trên khoảng cách ngón tay.
    * 🕹️ **Tay Phải:** Điều hướng (Joystick ảo) theo vector vị trí tay.
* **Smoothing Algorithm:** Tích hợp bộ lọc nhiễu giúp xe di chuyển mượt mà, không bị giật cục.
* **AI Vision:** Nhận diện bàn tay chính xác bằng Google MediaPipe (Model Lite).

### 🎥 Video Demo
[Demo Link](https://drive.google.com/file/d/1zi9xEzxrtOBP-PK36ziJwcpSPLFUbvFv/view?usp=sharing)

## 📂 Cấu trúc dự án

* `control_new.py`: Mã nguồn Python chạy trên máy tính. Xử lý hình ảnh, vẽ HUD và gửi lệnh UDP.
* `hand_controlling_mecanum_own_self_wifi.ino`: Mã nguồn C++ nạp cho ESP32. Nhận UDP và điều khiển động cơ.
* `environments.yaml`: File cấu hình môi trường Anaconda (các thư viện cần thiết).

## 🛠️ Yêu cầu phần cứng

1.  **Mạch điều khiển:** ESP32 (DevKit V1 hoặc tương đương).
2.  **Khung xe:** Mecanum Wheel Chassis (4 bánh).
3.  **Driver động cơ:** L298N hoặc Motor Shield tương thích.
4.  **Nguồn:** Pin Li-ion 18650 (2s hoặc 3s).
5.  **Máy tính:** Có Webcam.

### Sơ đồ nối dây (ESP32)
Dựa trên firmware:
* **Trước Trái (FL):** Chân 18, 19
* **Trước Phải (FR):** Chân 17, 5
* **Sau Trái (BL):** Chân 14, 12
* **Sau Phải (BR):** Chân 26, 27

## ⚙️ Cài đặt & Thiết lập

### 1. Phần Mềm (Máy tính)

Sử dụng **Anaconda** hoặc **Miniconda** để cài đặt môi trường tránh xung đột thư viện.

```bash
# 1. Clone dự án này về máy
git clone <your-repo-link>
cd <your-repo-folder>

# 2. Tạo môi trường từ file .yaml
conda env create -f environments.yaml

# 3. Kích hoạt môi trường
conda activate robot_arm
```

### 2. Phần Cứng (ESP32)

1.  Mở file `hand_controlling_mecanum_own_self_wifi.ino` bằng Arduino IDE.
2.  Cài đặt board **ESP32 Dev Module** trong Board Manager.
3.  Nạp code vào ESP32.

## 🚀 Hướng dẫn sử dụng

### Bước 1: Khởi động xe
Sau khi cấp nguồn, ESP32 sẽ tự phát ra một mạng Wifi.
* **SSID:** `FPTU_Can_Tho_Mecanum_Car_2`
* **Password:** `fptucantho`

### Bước 2: Kết nối máy tính
Sử dụng máy tính (laptop) kết nối vào mạng Wifi trên.

### Bước 3: Chạy trình điều khiển
Mở Terminal (trong môi trường conda đã kích hoạt) và chạy:

```bash
python control_new.py
```
*IP mặc định của xe là `192.168.4.1` và Port `4212`.*

### Bước 4: Điều khiển

Giao diện HUD sẽ hiện lên. Đứng trước Webcam và đưa tay vào khung hình:

#### 🖐 TAY TRÁI (Tay Ga)
* Đưa tay vào vùng bên trái.
* **Chụm (Cái + Trỏ):** Điều khiển tốc độ.
    * **Mở rộng:** Tốc độ cao (Max 165).
    * **Khép lại:** Tốc độ thấp / Dừng.

#### 🕹️ TAY PHẢI (Tay Lái)
Đưa tay vào vùng bên phải. Số lượng ngón tay quyết định Chế độ (Mode):

| Số ngón tay | Chế độ | Hành động |
| :--- | :--- | :--- |
| **5 ngón (Xòe)** | **STOP** | Dừng khẩn cấp. |
| **0 hoặc 1 ngón (Nắm)** | **XOAY** | Đưa nắm đấm sang Trái/Phải để xoay xe. |
| **3 ngón (Cái, Trỏ, Giữa)** | **ĐI THẲNG** | Đưa tay Lên, Xuống, Trái, Phải để di chuyển. |
| **3 ngón (Giữa, Áp, Út)** | **ĐI CHÉO** | Đưa tay về 4 góc để đi chéo (Drift). |

## 👨‍💻 Tác giả
**Sinh viên:** [Tên của bạn]
**Trường:** Đại học FPT Cần Thơ

**Chuyên ngành:** Trí tuệ nhân tạo (AI)
