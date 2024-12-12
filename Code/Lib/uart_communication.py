import serial
import time
import cv2
import numpy as np
import math
from scipy.spatial import distance

class UARTCommunication:
    def __init__(self, port, baudrate=115200, timeout=None):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Đợi ESP8266 khởi động giao tiếp

    def send_command(self, command):
        """Gửi lệnh đến ESP8266"""
        if self.serial.is_open:
            command_with_terminator = f"{command}\n"
            self.serial.write(command_with_terminator.encode())

    def read_response(self, onreset = True):
        """Đọc phản hồi từ ESP8266"""
        if self.serial.is_open:
            try:
                if onreset:
                    # Làm sạch bộ đệm trước khi nhận dữ liệu mới
                    self.serial.reset_input_buffer()  # Xóa bộ đệm
                # Lấy dữ liệu dòng đầu tiên
                raw_response = self.serial.readline()  # Đọc dữ liệu gốc (dạng bytes)

                try:
                    # Giải mã dữ liệu thành utf-8
                    decoded_response = raw_response.decode("utf-8").strip()
                except UnicodeDecodeError:
                    # Không thể giải mã nếu dữ liệu không phải chuỗi UTF-8
                    print("Dữ liệu không phải chuỗi UTF-8.")
                    return None

                print(decoded_response)

                # Kiểm tra định dạng dữ liệu
                if decoded_response.startswith("RFID|"):
                    # Sau khi nhận dữ liệu thì làm sạch bộ đệm
                    self.serial.reset_input_buffer()  # Xóa bộ đệm
                    # Lấy ID RFID
                    line = decoded_response.split('|')
                    if len(line) == 2 and len(line[1]) == 8:
                        return {"type": "RFID", "data": line[1]}
                elif decoded_response.startswith("FINGERTEMPLATE|"):
                    # Lấy mẫu vân tay
                    raw_template = self.serial.read(512) # Đọc 512 byte dữ liệu mẫu của vân tay
                     # Sau khi nhận dữ liệu, làm sạch bộ đệm
                    self.serial.reset_input_buffer()  # Xóa bộ đệm
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
    similarity = 1 - distance.cosine(vector1, vector2) # Tính góc cosine giữa 2 vector
    return similarity

############################## Thuật toán Minutiae-based Matching ##################################
def improved_fingerprint_matching(template1, template2, threshold=0.6):
    def extract_minutiae_details(template):
        minutiae = []
        # Giải mã chi tiết từng điểm minutiae
        for i in range(0, 512, 32):  # Giả sử mỗi minutiae 32 byte
            x = (template[i] << 8) | template[i+1]
            y = (template[i+2] << 8) | template[i+3]
            angle = template[i+4]
            minutiae_type = template[i+5]  # 0: đầu, 1: nhánh

            minutiae.append({
                'x': x,
                'y': y,
                'angle': angle,
                'type': minutiae_type
            })
        return minutiae

    def calculate_minutiae_match(point1, point2):
        # Tính khoảng cách
        distance = math.sqrt((point1['x'] - point2['x'])**2 +
                             (point1['y'] - point2['y'])**2)

        # Kiểm tra góc và loại điểm
        angle_diff = abs(point1['angle'] - point2['angle'])
        type_match = point1['type'] == point2['type']

        # Điều kiện khớp: khoảng cách < 10, góc chênh lệch < 15, cùng loại
        return (distance < 10 and
                angle_diff < 15 and
                type_match)

    # Trích xuất minutiae
    minutiae1 = extract_minutiae_details(template1)
    minutiae2 = extract_minutiae_details(template2)

    # Đếm số điểm khớp
    match_count = 0
    for point1 in minutiae1:
        for point2 in minutiae2:
            if calculate_minutiae_match(point1, point2):
                match_count += 1
                break

    # Tỉ lệ khớp
    match_ratio = match_count / len(minutiae1)

    # So sánh với ngưỡng
    return match_ratio >= threshold, match_ratio

############################## End thuật toán Minutiae-based Matching ##################################

if __name__ == "__main__":
    listFingerTemplate = [b'0', b'0']
    uart = UARTCommunication(port="COM4", baudrate=115200, timeout=5)
    count = 1
    flag = 0
    uart.send_command("GET_FINGERPRINT1")
    while True:
        try:
            # Gửi lệnh yêu cầu dữ liệu
            # uart.send_command("GET_DATA")
            count = 1 - count
            flag += 1
            print(count)
            time.sleep(1)
            response = uart.read_response()
            if response:
                if response["type"] == "RFID":
                    print(f"Nhận được RFID ID: {response['data']}")
                    listFingerTemplate[count] = response['data']
                elif response["type"] == "FINGERPRINT":
                    print(f"Dữ liệu vân tay: {count}")
                    listFingerTemplate[count] = response["data"]
                    print(f"Nhận được dữ liệu mẫu vân tay ({len(response['data'])} byte)")
            else:
                print("Không nhận được phản hồi hợp lệ.")

            if flag % 2 == 0:
                if len(listFingerTemplate[0]) == 512 and len(listFingerTemplate[1]) == 512:
                    print(f"{listFingerTemplate[0].hex()} - {listFingerTemplate[1].hex()}")
                    match_score = improved_fingerprint_matching(listFingerTemplate[0], listFingerTemplate[1], threshold=0.6)
                    jaccard_score = jaccard_index(listFingerTemplate[0], listFingerTemplate[1])
                    similarity = cosine_similarity(listFingerTemplate[0], listFingerTemplate[1])
                    print(f"Tỉ lệ trùng khớp với phương pháp jaccard: {jaccard_score}")
                    print(f"Tỉ lệ trùng với phương pháp cosine similarity: {similarity}")
                    print(f"Tỉ lệ trùng với thuật toán Minutiae-based Matching: {match_score}")
                    print(isinstance(listFingerTemplate[0], bytes))

        finally:
            # Đóng kết nối UART
            # uart.close()
            pass
