import cv2
import mediapipe as mp
import math
import socket
import numpy as np
from collections import Counter # <--- MỚI THÊM: Thư viện đếm lệnh

# --- CẤU HÌNH KẾT NỐI ---
ESP_IP = "192.168.4.1" 
ESP_PORT = 4212
MAX_SPEED = 165
DEADZONE = 50 
SPLIT_RATIO = 0.35 # 35% màn hình trái cho tay ga

# --- CẤU HÌNH BỘ LỌC NHIỄU (MỚI THÊM) ---
HISTORY_SIZE = 5  # Số lượng khung hình lưu lại để lọc
cmd_history = []  # Danh sách lưu lịch sử lệnh

# --- MÀU SẮC (Bảng màu Neon Sci-fi) ---
COLOR_CYAN = (255, 255, 0)      # Màu xanh ngọc (Giao diện chính)
COLOR_GREEN = (0, 255, 0)       # Màu xanh lá (Đi thẳng/An toàn)
COLOR_RED = (0, 0, 255)         # Màu đỏ (Dừng/Cảnh báo)
COLOR_ORANGE = (0, 165, 255)    # Màu cam (Đi chéo)
COLOR_PURPLE = (255, 0, 255)    # Màu tím (Xoay)
COLOR_DARK = (20, 20, 20)       # Màu nền mờ

# Thiết lập UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Hàm vẽ chữ có bóng (cho dễ đọc)
def draw_text(img, text, pos, scale=1, color=(255,255,255), thickness=2):
    x, y = pos
    # Vẽ bóng đen
    cv2.putText(img, text, (x+2, y+2), cv2.FONT_HERSHEY_DUPLEX, scale, (0,0,0), thickness+1, cv2.LINE_AA)
    # Vẽ chữ chính
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, color, thickness, cv2.LINE_AA)

# Hàm vẽ thanh năng lượng (Throttle Bar)
def draw_power_bar(img, speed, max_speed, x, y, w, h):
    # Vẽ khung
    cv2.rectangle(img, (x, y), (x + w, y + h), COLOR_CYAN, 2)
    # Tính chiều cao cột pin dựa trên tốc độ
    fill_h = int((speed / max_speed) * h)
    # Vẽ phần pin (từ dưới lên)
    # Đổi màu pin: Xanh nếu nhanh, Vàng nếu chậm
    bar_color = COLOR_GREEN if speed > 50 else (0, 255, 255)
    if speed == 0: bar_color = (50, 50, 50)
    
    # Vẽ hình chữ nhật đặc
    cv2.rectangle(img, (x + 3, y + h - fill_h + 3), (x + w - 3, y + h - 3), bar_color, -1)
    
    # Số %
    percent = int((speed / max_speed) * 100)
    draw_text(img, f"{percent}%", (x, y - 10), 0.6, bar_color, 1)

# Hàm vẽ Joystick ảo
def draw_joystick_ui(img, center_x, center_y, hand_x, hand_y, mode, cmd):
    # Vẽ vòng tròn vùng chết (Deadzone) nét đứt
    cv2.circle(img, (center_x, center_y), DEADZONE, (100, 100, 100), 1, cv2.LINE_AA)
    
    # Chọn màu dựa trên chế độ
    if mode == "STOP": active_color = COLOR_RED
    elif mode == "ROTATE": active_color = COLOR_PURPLE
    elif mode == "DIAGONAL": active_color = COLOR_ORANGE
    else: active_color = COLOR_GREEN

    # Vẽ đường nối "dây thun" từ tâm đến tay
    cv2.line(img, (center_x, center_y), (hand_x, hand_y), active_color, 2, cv2.LINE_AA)
    
    # Vẽ tâm ngắm tại vị trí tay (Reticle)
    cv2.circle(img, (hand_x, hand_y), 20, active_color, 2, cv2.LINE_AA)
    cv2.circle(img, (hand_x, hand_y), 5, active_color, -1) # Chấm tâm
    
    # Vẽ 4 gạch ngắm xung quanh vòng tròn tay
    r = 30
    cv2.line(img, (hand_x - r, hand_y), (hand_x - r + 10, hand_y), active_color, 2)
    cv2.line(img, (hand_x + r, hand_y), (hand_x + r - 10, hand_y), active_color, 2)
    cv2.line(img, (hand_x, hand_y - r), (hand_x, hand_y - r + 10), active_color, 2)
    cv2.line(img, (hand_x, hand_y + r), (hand_x, hand_y + r - 10), active_color, 2)

    # Hiển thị lệnh to rõ
    draw_text(img, f"CMD: {cmd.upper()}", (center_x - 80, center_y + 120), 1, active_color, 2)
    draw_text(img, f"MODE: {mode}", (center_x - 80, center_y + 160), 0.7, (200, 200, 200), 1)

# Các hàm logic cũ (Map range, Finger count, Get Direction) giữ nguyên
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_fingers_status(lm, h, w):
    fingers = []
    if lm[4].x < lm[3].x: fingers.append(1)
    else: fingers.append(0)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for t, p in zip(tips, pips):
        if lm[t].y < lm[p].y: fingers.append(1)
        else: fingers.append(0)
    return fingers

def get_direction(angle, mode):
    if mode == "LINEAR":
        # SỬA LỖI 1: Đổi "forward" thành "fwd" để khớp với Arduino
        if -135 <= angle < -45: return "fwd"
        elif -45 <= angle < 45: return "right"
        elif 45 <= angle < 135: return "back"
        else: return "left"
        
    elif mode == "DIAGONAL":
        # SỬA LỖI 2: Đổi chữ Hoa thành chữ thường ("FR" -> "fr")
        # SỬA LỖI 3: Chỉnh lại logic góc phần tư
        if -90 <= angle < 0: return "fr"      # Phải trên (Front-Right)
        elif 0 <= angle < 90: return "br"     # Phải dưới (Back-Right)
        elif 90 <= angle < 180: return "bl"   # Trái dưới (Back-Left) <--- Lỗi cũ là "BR"
        else: return "fl"                     # Trái trên (Front-Left)
        
    return "stop"

# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # Tăng độ phân giải lên HD cho nét (nếu máy yếu thì về 800)
cap.set(4, 720)

with mp_hands.Hands(
    model_complexity=1, 
    min_detection_confidence=0.35, 
    min_tracking_confidence=0.4, 
    max_num_hands=2
) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # --- TẠO LỚP OVERLAY (KÍNH MỜ) ---
        overlay = frame.copy()
        
        # Tính toán tọa độ chia màn hình
        split_x = int(w * SPLIT_RATIO)
        joy_center_x = split_x + (w - split_x) // 2
        joy_center_y = h // 2
        
        # Vẽ nền tối cho 2 khu vực để chữ nổi bật
        cv2.rectangle(overlay, (0, 0), (split_x, h), (0, 0, 0), -1) # Vùng trái tối hơn
        cv2.rectangle(overlay, (split_x, 0), (w, 80), (0, 0, 0), -1) # Header tối
        
        # Áp dụng độ trong suốt (Alpha Blending)
        alpha = 0.4 # Độ mờ (0.0 - 1.0)
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Vẽ đường phân cách Neon
        cv2.line(frame, (split_x, 0), (split_x, h), COLOR_CYAN, 2)
        cv2.circle(frame, (split_x, h//2), 5, COLOR_CYAN, -1) # Điểm trang trí
        
        # Tiêu đề khu vực
        draw_text(frame, "THRUST CONTROL", (20, 40), 0.8, COLOR_CYAN, 2)
        draw_text(frame, "VECTOR NAVIGATOR", (split_x + 20, 40), 0.8, COLOR_GREEN, 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        current_cmd = "stop"
        current_speed = 0
        left_hand_active = False
        right_hand_active = False
        
        if results.multi_hand_landmarks:
            for hand_lm, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                cx, cy = int(hand_lm.landmark[9].x * w), int(hand_lm.landmark[9].y * h)
                
                # --- MỚI THÊM: Vẽ Keypoints để debug ---
                mp_drawing.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)

                # --- XỬ LÝ TAY TRÁI (GA) ---
                if label == 'Left':
                    if cx > split_x:
                        draw_text(frame, "WARNING: HAND OVERLAP", (cx-100, cy-50), 0.8, COLOR_RED, 2)
                    else:
                        left_hand_active = True
                        x4, y4 = int(hand_lm.landmark[4].x * w), int(hand_lm.landmark[4].y * h)
                        x8, y8 = int(hand_lm.landmark[8].x * w), int(hand_lm.landmark[8].y * h)
                        dist = math.hypot(x8-x4, y8-y4)
                        
                        # Vẽ đường đo khoảng cách ngón tay
                        cv2.line(frame, (x4, y4), (x8, y8), COLOR_CYAN, 2)
                        
                        if dist < 20: current_speed = 0
                        else:
                            current_speed = int(map_range(dist, 20, 200, 0, MAX_SPEED))
                            if current_speed > MAX_SPEED: current_speed = MAX_SPEED
                        
                        # VẼ THANH POWER BAR "NGẦU"
                        draw_power_bar(frame, current_speed, MAX_SPEED, 50, 100, 60, 400)

                # --- XỬ LÝ TAY PHẢI (LÁI) ---
                if label == 'Right':
                    # --- RÀNG BUỘC QUAN TRỌNG: CHỈ NHẬN JOYSTICK KHI TAY Ở BÊN PHẢI ---
                    if cx < split_x:
                        # Nếu tay phải (hoặc tay bị nhận diện nhầm) lấn sang vùng Throttle
                        # -> BỎ QUA NGAY LẬP TỨC
                        continue 

                    right_hand_active = True
                    fingers = get_fingers_status(hand_lm.landmark, h, w)
                    total_fingers = fingers.count(1)
                    
                    mode = "UNKNOWN"
                    
                    if total_fingers == 5:
                        mode = "STOP"
                        current_cmd = "stop"
                    elif total_fingers == 0 or (total_fingers == 1 and fingers[0]==1):
                        mode = "ROTATE"
                        if cx < joy_center_x - DEADZONE: current_cmd = "ccw"
                        elif cx > joy_center_x + DEADZONE: current_cmd = "cw"
                        else: current_cmd = "stop"
                    elif fingers[0]==1 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0 and fingers[4]==0:
                        mode = "LINEAR"
                    elif fingers[2]==1 and fingers[3]==1 and fingers[4]==1 and fingers[1]==0:
                        mode = "DIAGONAL"
                    
                    if mode in ["LINEAR", "DIAGONAL"]:
                        dx = cx - joy_center_x
                        dy = cy - joy_center_y
                        dist_center = math.hypot(dx, dy)
                        if dist_center < DEADZONE: current_cmd = "stop"
                        else:
                            angle = math.degrees(math.atan2(dy, dx))
                            current_cmd = get_direction(angle, mode)
                    
                    # VẼ JOYSTICK UI XỊN XÒ
                    draw_joystick_ui(frame, joy_center_x, joy_center_y, cx, cy, mode, current_cmd)

        # --- MỚI THÊM: LOGIC LỌC NHIỄU (HISTORY FILTER) ---
        cmd_history.append(current_cmd)
        if len(cmd_history) > HISTORY_SIZE:
            cmd_history.pop(0)
        
        # Tìm lệnh xuất hiện nhiều nhất trong 5 khung hình gần nhất
        filtered_cmd = Counter(cmd_history).most_common(1)[0][0]

        # Gửi dữ liệu UDP (Sử dụng filtered_cmd thay vì current_cmd)
        if left_hand_active or right_hand_active:
            if not left_hand_active: current_speed = 0
            
            # Gửi lệnh ĐÃ LỌC đi
            msg = f"{filtered_cmd},{current_speed}"
            sock.sendto(msg.encode(), (ESP_IP, ESP_PORT))
        else:
            # Xóa lịch sử để reset bộ lọc khi không có tay
            cmd_history.clear()
            sock.sendto("stop,0".encode(), (ESP_IP, ESP_PORT))
            draw_text(frame, "NO SIGNAL - SYSTEM IDLE", (w//2 - 150, h - 50), 0.8, (100,100,100), 2)

        cv2.imshow("Mecanum HUD System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()