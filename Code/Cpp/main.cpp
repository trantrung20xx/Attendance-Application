#include <Adafruit_Fingerprint.h>
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <MFRC522.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <Wire.h>

// Địa chỉ I2C của LCD (có thể là 0x27 hoặc 0x3F, tùy theo loại LCD)
#define LCD_ADDRESS 0x27
// Khởi tạo LCD: 16 cột, 2 dòng
LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);

#define SS_PIN  15 // D8
#define RST_PIN 16 // D0

// LCD1602 I2C
#define SDA_PIN 2 // D4
#define SCK_PIN 0 // D3

// RFID
MFRC522 rfid(SS_PIN, RST_PIN); // Tạo đối tượng của lớp MFRC522

uint8_t UID[4]; // Mảng chứa UID của thẻ rfid

// Cảm biến vân tay
#define RX_PIN D2 // GPIO4
#define TX_PIN D1 // GPIO5

SoftwareSerial       mySerial(RX_PIN, TX_PIN); // Sử dụng UART (RX: D2, TX: D1) của ESP8266
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// Hàm gửi mẫu vân tay đọc được qua UART
bool sendFingerprintTemplate(void);

// Khai báo biến
String uidString = "";
String command   = "";

void setup() {
    Serial.begin(115200);
    Wire.begin(SDA_PIN, SCK_PIN); // Khởi tạo giao tiếp I2C với LCD
    lcd.init();                   // Khởi tạo màn hình LCD
    lcd.backlight();              // Bật đèn nền LCD
    SPI.begin();                  // Khởi tạo giao tiếp SPI
    rfid.PCD_Init();              // Khởi tạo MFRC522
    // mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);  // Khởi tạo kết nối UART
    finger.begin(57600); // Khởi tạo kết nối UART cho cảm biến vân tay
    delay(5);            // Đợi quá trình khởi tạo hoàn tất
    // Kiểm tra cảm biến vân tay
    if (finger.verifyPassword()) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Finger Ok");
    } else {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Finger Fail");
    }
    lcd.setCursor(0, 1);
    lcd.print("RFID Ok");
}

void loop() {
    // Đọc lệnh từ UART
    if (Serial.available() > 0) {
        command = Serial.readStringUntil('\n');
        command.trim();
    }
    processCommand(command);
    delay(350);
}

// Xử lý lệnh từ Python
void processCommand(String cmd) {
    if (cmd == "GET_RFID") {
        readRFID();
        lcd.setCursor(0, 0);
        lcd.print("RFID Done!");
    } else if (cmd == "GET_FINGERPRINT1" || cmd == "GET_FINGERPRINT2") {
        if (sendFingerprintTemplate()) {
            lcd.setCursor(0, 0);
            lcd.print("Done!      ");
        }
    } else if (cmd == "GET_DATA") {
        readRFID();
        sendFingerprintTemplate();
    }
}

// Đọc RFID
void readRFID() {
    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
        return;
    }

    for (byte i = 0; i < rfid.uid.size; ++i) {
        UID[i] = rfid.uid.uidByte[i];
        uidString += String(UID[i], HEX); // Chuyển từng byte thành chuỗi HEX
    }

    if (uidString != "") {
        Serial.print("RFID|");     // Gửi dữ liệu header lên máy tính (UART)
        Serial.println(uidString); // Gửi dữ liệu lên máy tính (UART)
        // Làm sạch bộ đệm sau mỗi lần gửi
        Serial.flush();
        uidString = "";
    }

    // Halt PICC (Dừng đọc)
    rfid.PICC_HaltA();
    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();
}

// Hàm gửi mẫu vân tay đọc được qua UART
bool sendFingerprintTemplate() {
    if (finger.getImage() != FINGERPRINT_OK) { // Nếu không có vân tay đặt vào cảm biến
        return false;
    }

    if (finger.image2Tz(1) != FINGERPRINT_OK) { // Chuyển ảnh thành mẫu vân tay
        return false;
    }

    // Lấy dữ liệu mẫu từ buffer của cảm biến
    if (finger.getModel() != FINGERPRINT_OK) {
        return false;
    }

    uint8_t bytesReceived[534]; // Bộ đệm chứa dữ liệu mẫu
    memset(bytesReceived, 0xFF, 534);

    uint32_t startTime = millis();
    int      i         = 0;
    // Nhận toàn bộ gói dữ liệu mẫu vân tay (534 byte) trong buffer của cảm biến
    while (i < 534 && (millis() - startTime) < 10000) {
        if (mySerial.available()) {
            bytesReceived[i++] = mySerial.read();
        }
    }
    // Kiểm tra tính hợp lệ của dữ liệu
    if (i != 534) {
        return false;
    }

    uint8_t fingerTemplate[512]; // Mẫu vân tay thực sự
    memset(fingerTemplate, 0xFF, 512);

    // Chỉ lấy dữ liệu mẫu vân tay
    uint16_t uindx = 9, index = 0;
    // Đọc 256 byte đầu tiên bỏ qua 9 byte header
    memcpy(fingerTemplate + index, bytesReceived + uindx, 256);
    uindx += 256; // skip data
    uindx += 2;   // skip checksum
    uindx += 9;   // skip next header
    index += 256; // advance pointer
    // Đọc tiếp 256 byte vào mảng fingerTemplate
    memcpy(fingerTemplate + index, bytesReceived + uindx, 256);

    // Gửi dữ liệu qua UART tới máy tính
    Serial.println("FINGERTEMPLATE|"); // Gửi tiền tố
    Serial.write(fingerTemplate, 512);
    Serial.println();
    // Làm sạch bộ đệm sau mỗi lần gửi
    Serial.flush();

    return true;
}
