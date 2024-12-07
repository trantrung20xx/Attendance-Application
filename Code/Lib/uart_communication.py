import serial
import time

class UARTCommunication:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Đợi ESP8266 khởi động giao tiếp

    def send_command(self, command):
        """Gửi lệnh đến ESP8266"""
        if self.serial.is_open:
            command_with_terminator = f"{command}\n"
            self.serial.write(command_with_terminator.encode())

    def read_response(self):
        """Đọc phản hồi từ ESP8266"""
        if self.serial.is_open:
            try:
                raw_response = self.serial.readline().decode().strip()
                print(raw_response)
                # Kiểm tra định dạng dữ liệu
                if raw_response.startswith("RFID|"):
                    # Sau khi nhận dữ liệu, làm sạch bộ đệm
                    self.serial.flush()  # Xóa bộ đệm
                    # Lấy ID RFID
                    line = raw_response.split('|')
                    if len(line) == 2 and len(line[1]) == 8:
                        return {"type": "RFID", "data": line[1]}
                elif raw_response.startswith("FINGERTEMPLATE|"):
                    # Lấy mẫu vân tay
                    raw_template = self.serial.read(512) # Đọc 512 byte dữ liệu mẫu của vân tay
                     # Sau khi nhận dữ liệu, làm sạch bộ đệm
                    self.serial.flush()  # Xóa bộ đệm
                    return {"type": "FINGERPRINT", "data": raw_template}
                else:
                    return None
            except Exception as e:
                print(f"Lỗi khi đọc phản hồi: {e}")
                return None

    def close(self):
        """Đóng giao tiếp UART"""
        if self.serial.is_open:
            self.serial.close()

if __name__ == "__main__":
    listFingerTemplate = [b'0', b'0']
    uart = UARTCommunication(port="COM4", baudrate=115200, timeout=10)
    count = 1
    flag = 0
    while True:
        try:
            # Gửi lệnh yêu cầu dữ liệu
            # uart.send_command("GET_DATA")
            count = 1 - count
            flag += 1
            print(count)
            time.sleep(1)

            # Đọc phản hồi từ ESP32
            response = uart.read_response()
            if response:
                if response["type"] == "RFID":
                    print(f"Nhận được RFID ID: {response['data']}")
                    listFingerTemplate[count] = response['data']
                elif response["type"] == "FINGERPRINT":
                    print(f"Dữ liệu vân tay: {response['data']}")
                    listFingerTemplate[count] = response["data"]
                    print(f"Nhận được dữ liệu mẫu vân tay ({len(response['data'])} byte)")
            else:
                print("Không nhận được phản hồi hợp lệ.")

            if flag % 2 == 0:
                print(f"{listFingerTemplate[0]} - {listFingerTemplate[1]}")
                print(listFingerTemplate[0] == listFingerTemplate[1])

        finally:
            # Đóng kết nối UART
            # uart.close()
            pass
