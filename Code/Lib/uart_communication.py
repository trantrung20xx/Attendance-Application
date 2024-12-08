import serial
import time
from scipy.spatial.distance import cosine

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

def jaccard_index(data1, data2):
    """
        Tính chỉ số jaccard giữa 2 mẫu nhị phân
        Tính toán bằng công thức: J(A, B) = |A & B| / |A | B |
        Với:
            |A & B|: Số bit giống nhau
            |A | B|: Số bit khác nhau
    """
    if len(data1) == len(data2):
        intersection = sum(bin(byte1 & byte2).count('1') for byte1, byte2 in zip(data1, data2))
        union = sum(bin(byte1 | byte2).count('1') for byte1, byte2 in zip(data1, data2))
        return intersection / union # Trả về tỉ lệ các bit chung giữa 2 mẫu
    else:
        print("Hai mẫu phải bằng nhau để so sánh")

def cosine_similarity(data1, data2):
    """
        Tính độ tương đồng Cosine giữa 2 mẫu
        Tính góc cosine giữa 2 vector
        Nếu:
            góc gần 0 độ thì hai muẫu rất giống nhau (độ tương đồng gần 1)
            góc gần 90 độ thì hai mẫu rất khác nhau (độ tương đồng gần 0)
    """
    # Chuyển thành vector số
    vector1 = list(data1)
    vector2 = list(data2)
    # Tính độ tương đồng (khoảng cách của 2 mẫu dữ liệu)
    similarity = 1 - cosine(vector1, vector2) # Tính góc cosine giữa 2 vector
    return similarity

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
                if len(listFingerTemplate[0]) == 512 and len(listFingerTemplate[1]) == 512:
                    print(f"{listFingerTemplate[0]} - {listFingerTemplate[1]}")
                    jaccard_score = jaccard_index(listFingerTemplate[0], listFingerTemplate[1])
                    similarity = cosine_similarity(listFingerTemplate[0], listFingerTemplate[1])
                    print(f"Tỉ lệ trùng khớp với phương pháp jaccard: {jaccard_score}")
                    print(f"Tỉ lệ trùng với với phương pháp cosine similarity: {similarity}")

        finally:
            # Đóng kết nối UART
            # uart.close()
            pass
