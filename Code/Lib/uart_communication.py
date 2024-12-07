import serial
import time

class UARTCommunication:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Đợi ESP32 khởi động giao tiếp

    def send_command(self, command):
        """Gửi lệnh đến ESP32"""
        if self.serial.is_open:
            command_with_terminator = f"{command}\n"  # Thêm ký tự xuống dòng
            self.serial.write(command_with_terminator.encode())

    def read_response(self):
        """Đọc phản hồi từ ESP32"""
        if self.serial.is_open:
            try:
                response = self.serial.readline().decode().strip()
                return response
            except Exception as e:
                print(f"Lỗi khi đọc phản hồi: {e}")
                return None

    def close(self):
        """Đóng giao tiếp UART"""
        if self.serial.is_open:
            self.serial.close()
