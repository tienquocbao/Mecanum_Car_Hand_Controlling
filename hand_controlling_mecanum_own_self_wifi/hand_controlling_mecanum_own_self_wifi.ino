#include <WiFi.h>
#include <WiFiUdp.h>

// --- CẤU HÌNH WIFI TỰ PHÁT (AP) ---
const char* ssid = "FPTU_Can_Tho_Mecanum_Car_2";  // Tên Wifi xe sẽ phát ra
const char* password = "fptucantho";     // Mật khẩu
const int localPort = 4212;

WiFiUDP Udp;
char packetBuffer[255];

// --- KHAI BÁO CHÂN MOTOR (GIỮ NGUYÊN) ---
const int FL_1 = 18; const int FL_2 = 19; 
const int FR_1 = 17; const int FR_2 = 5;
const int BL_1 = 14; const int BL_2 = 12;
const int BR_1 = 26; const int BR_2 = 27;

// --- CẤU HÌNH ĐỘ MƯỢT ---
const int ACCEL_STEP = 8; 
const unsigned long ACCEL_DELAY = 10; 

float currentSpeed[4] = {0, 0, 0, 0};
int targetSpeed[4]  = {0, 0, 0, 0};
unsigned long lastAccelTime = 0;

// --- HÀM MOTOR ---
void writeMotor(int p1, int p2, int speed) {
  if (speed > 0) { analogWrite(p1, speed); analogWrite(p2, 0); }
  else if (speed < 0) { analogWrite(p1, 0); analogWrite(p2, -speed); }
  else { analogWrite(p1, 0); analogWrite(p2, 0); }
}

void setTarget(int fl, int fr, int bl, int br, int speedVal) {
  targetSpeed[0] = fl * speedVal; targetSpeed[1] = fr * speedVal;
  targetSpeed[2] = bl * speedVal; targetSpeed[3] = br * speedVal;
}

// --- XỬ LÝ GÓI TIN ---
void processPacket(String msg) {
  int commaIndex = msg.indexOf(',');
  if (commaIndex == -1) return;
  String cmd = msg.substring(0, commaIndex);
  int spd = msg.substring(commaIndex + 1).toInt();
  if (spd > 165) spd = 165; if (spd < 0) spd = 0;

  if (cmd == "stop")       setTarget(0, 0, 0, 0, 0);
  else if (cmd == "fwd")   setTarget(1, 1, 1, 1, spd);
  else if (cmd == "back")  setTarget(-1, -1, -1, -1, spd);
  else if (cmd == "left")  setTarget(-1, 1, 1, -1, spd);
  else if (cmd == "right") setTarget(1, -1, -1, 1, spd);
  else if (cmd == "fl")    setTarget(0, 1, 1, 0, spd);
  else if (cmd == "fr")    setTarget(1, 0, 0, 1, spd);
  else if (cmd == "bl")    setTarget(-1, 0, 0, -1, spd);
  else if (cmd == "br")    setTarget(0, -1, -1, 0, spd);
  else if (cmd == "cw")    setTarget(1, -1, 1, -1, spd);
  else if (cmd == "ccw")   setTarget(-1, 1, -1, 1, spd);
}

void setup() {
  Serial.begin(115200);
  pinMode(FL_1, OUTPUT); pinMode(FL_2, OUTPUT);
  pinMode(FR_1, OUTPUT); pinMode(FR_2, OUTPUT);
  pinMode(BL_1, OUTPUT); pinMode(BL_2, OUTPUT);
  pinMode(BR_1, OUTPUT); pinMode(BR_2, OUTPUT);

  // --- THIẾT LẬP AP MODE ---
  Serial.println("Dang tao Wifi...");
  WiFi.softAP(ssid, password); // Lệnh quan trọng nhất: Tự phát Wifi
  
  Serial.print("Wifi Name: "); Serial.println(ssid);
  Serial.print("IP Address: "); 
  Serial.println(WiFi.softAPIP()); // Thường sẽ là 192.168.4.1

  Udp.begin(localPort);
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    processPacket(String(packetBuffer));
  }

  unsigned long currentMillis = millis();
  if (currentMillis - lastAccelTime >= ACCEL_DELAY) {
    lastAccelTime = currentMillis;
    for (int i = 0; i < 4; i++) {
      if (currentSpeed[i] < targetSpeed[i]) currentSpeed[i] += ACCEL_STEP;
      else if (currentSpeed[i] > targetSpeed[i]) currentSpeed[i] -= ACCEL_STEP;
      if (abs(currentSpeed[i] - targetSpeed[i]) < ACCEL_STEP) currentSpeed[i] = targetSpeed[i];
    }
    writeMotor(FL_1, FL_2, (int)currentSpeed[0]);
    writeMotor(FR_1, FR_2, (int)currentSpeed[1]);
    writeMotor(BL_1, BL_2, (int)currentSpeed[2]);
    writeMotor(BR_1, BR_2, (int)currentSpeed[3]);
  }
}