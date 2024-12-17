import serial
import time
import cv2
import numpy as np
import math
from scipy.spatial import distance
import ctypes
import os

class UARTCommunication:
    def __init__(self, port, baudrate=115200, timeout=None):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Đợi ESP8266 khởi động giao tiếp

    def send_command(self, command, endline = True, number = False):
        """Gửi lệnh đến ESP8266"""
        if self.serial.is_open:
            command_with_terminator = f"{command}\n" if endline else command
            if not number:
                self.serial.write(command_with_terminator.encode())
            else:
                data = bytearray()
                if isinstance(command, bytes): # Nếu là kiểu bytes
                    data.append(int(command[0]))
                elif isinstance(command, int): # Nếu là kiểu int
                    data.append(command_with_terminator)
                else:
                    raise ValueError("Command must be either bytes or int.")
                self.serial.write(bytes(data))
    def read_response(self, onreset = True):
        from Lib import message_uart
        """Đọc phản hồi từ ESP8266"""
        if self.serial.is_open:
            try:
                if onreset:
                    # Làm sạch bộ đệm trước khi nhận dữ liệu mới
                    self.serial.reset_input_buffer()  # Xóa bộ đệm
                # Lấy dữ liệu dòng đầu tiên
                raw_response = self.serial.readline()  # Đọc dữ liệu gốc (dạng bytes)
                if raw_response == b'\n':
                    message_uart[0] = None
                    return None

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
                    if len(line) == 2 and (len(line[1]) in [6, 7, 8]):
                        return {"type": "RFID", "data": line[1]}
                elif decoded_response.startswith("FINGERPRINT|"):
                    # Lấy mẫu vân tay
                    # raw_template = self.serial.read(512) # Đọc 512 byte dữ liệu mẫu của vân tay
                    # if len(raw_template) == 512: # Kiểm tra độ dài dữ liệu
                    fingerprint_id = self.serial.read(1) # Đọc 1 byte dữ liệu ID của vân tay
                    print("ID: ", fingerprint_id)
                    # Sau khi nhận dữ liệu, làm sạch bộ đệm
                    self.serial.reset_input_buffer()  # Xóa bộ đệm
                    if len(fingerprint_id) == 1: # Kiểm tra độ dài dữ liệu
                        return {"type": "FINGERPRINT", "data": fingerprint_id}
                    else:
                        # print(f"Lỗi: Nhận được {len(raw_template)} byte, không đủ 512 byte.")
                        print(f"Lỗi: Nhận được {len(fingerprint_id)} byte, Yêu cầu 1 byte.")
                        return None
                else:
                    message_uart[0] = decoded_response
                    return None
            except Exception as e:
                print(f"Lỗi khi đọc phản hồi: {e}")
                return None

    def close(self):
        """Đóng giao tiếp UART"""
        if self.serial.is_open:
            self.serial.close()

def hamming_distance(fingerprint1, fingerprint2, threshold=90):
    if len(fingerprint1) != len(fingerprint2):
        raise ValueError("Fingerprint templates must have the same length")

    t1 = np.unpackbits(np.frombuffer(fingerprint1, dtype=np.uint8))
    t2 = np.unpackbits(np.frombuffer(fingerprint2, dtype=np.uint8))

    max_bits = len(fingerprint1) * 8
    hamming_dist = sum(t1 != t2)

    confidence = max(0, 100 * (1 - hamming_dist / max_bits))
    return confidence >= threshold, confidence

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

def cosine_similarity(data1, data2, threshold=0.8):
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
    dot_product = sum(vector1[i] * vector2[i] for i in range(len(vector1)))
    magnitude_a = math.sqrt(sum(x**2 for x in vector1))
    magnitude_b = math.sqrt(sum(x**2 for x in vector2))

    if magnitude_a == 0 or magnitude_b == 0:
        return 1 - 1.0
    # similarity = 1 - distance.cosine(vector1, vector2) # Tính góc cosine giữa 2 vector
    # return similarity >= threshold, similarity
    return (1 - (dot_product / (magnitude_a * magnitude_b))) > threshold, 1 - (dot_product / (magnitude_a * magnitude_b))

def compare_templates(template1, template2):
        """
        So sánh hai mẫu vân tay và trả về mức độ tương đồng (%).
        Dựa trên thuật toán XOR để đo sự khác biệt.
        """
        diff = np.sum(template1 != template2)  # Đếm số byte khác nhau
        similarity = (1 - diff / len(template1)) * 100  # Tỷ lệ tương đồng (%)
        return similarity

############################## Thuật toán Minutiae-based Matching ##################################
def minutiae_based_matching(template1, template2, threshold=0.6):
    # Hàm trích xuất minutiae từ mẫu vân tay
    def extract_minutiae_details(template):
        minutiae = []
        for i in range(0, len(template), 8):  # Mỗi minutiae chiếm 8 byte
            x = (template[i] << 8) | template[i+1]    # Tọa độ x (2 byte)
            y = (template[i+2] << 8) | template[i+3]  # Tọa độ y (2 byte)
            angle = template[i+4]                     # Góc (1 byte)
            minutiae_type = template[i+5]             # Loại minutiae (0: đầu, 1: nhánh)
            minutiae.append({
                'x': x,
                'y': y,
                'angle': angle,
                'type': minutiae_type
            })
        return minutiae

    # Hàm tính toán sự khớp giữa 2 minutiae
    def calculate_minutiae_match(point1, point2):
        # Tính khoảng cách Euclidean giữa 2 minutiae
        distance = math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

        # Kiểm tra góc giữa 2 minutiae
        angle_diff = abs(point1['angle'] - point2['angle'])
        if angle_diff > 180:  # Đảm bảo góc lệch không quá 180 độ
            angle_diff = 360 - angle_diff

        # Kiểm tra loại minutiae (phải giống nhau: cả hai đều là đầu hoặc nhánh)
        type_match = point1['type'] == point2['type']

        # Điều kiện khớp: khoảng cách < 10 pixel, góc lệch < 20 độ, loại minutiae phải giống nhau
        return (distance < 10 and
                angle_diff < 20 and
                type_match)

    # Trích xuất minutiae từ 2 mẫu vân tay
    minutiae1 = extract_minutiae_details(template1)
    minutiae2 = extract_minutiae_details(template2)

    # Đếm số minutiae khớp
    match_count = 0
    for point1 in minutiae1:
        for point2 in minutiae2:
            if calculate_minutiae_match(point1, point2):
                match_count += 1
                break  # Một minutiae trong template1 đã khớp với một minutiae trong template2

    # Tính tỷ lệ khớp
    match_ratio = match_count / max(len(minutiae1), 1)  # Tránh chia cho 0

    # So sánh với ngưỡng để quyết định khớp hay không
    return match_ratio >= threshold, match_ratio

############################## End thuật toán Minutiae-based Matching ##################################

def cross_correlation(template1, template2, threshold=50):
    """
    Tính toán Cross-Correlation giữa hai mẫu vân tay

    :param template1: Mẫu vân tay thứ nhất (dạng bytes hoặc list)
    :param template2: Mẫu vân tay thứ hai (dạng bytes hoặc list)
    """
    # Chuyển dữ liệu sang numpy array
    t1 = np.frombuffer(template1, dtype=np.uint8)
    t2 = np.frombuffer(template2, dtype=np.uint8)

    # Tính toán giá trị Cross-Correlation
    mean_t1 = np.mean(t1)
    mean_t2 = np.mean(t2)
    numerator = np.sum((t1 - mean_t1) * (t2 - mean_t2))
    denominator = np.sqrt(np.sum((t1 - mean_t1) ** 2) * np.sum((t2 - mean_t2) ** 2))

    # cross_corr_value: Giá trị Cross-Correlation (-1 đến 1)
    cross_corr_value = numerator / denominator if denominator != 0 else 0

    # Tính toán độ tin cậy (0-100)
    confidence = max(0, min(100, (cross_corr_value + 1) * 50))

    return confidence >= threshold, confidence


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
            response = uart.read_response(onreset=False)
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
                    print(f"{listFingerTemplate[0]} - {listFingerTemplate[1]}")
                    jaccard_score = jaccard_index(listFingerTemplate[0], listFingerTemplate[1])
                    ret, similarity = cosine_similarity(listFingerTemplate[0], listFingerTemplate[1])
                    match_score = minutiae_based_matching(listFingerTemplate[0], listFingerTemplate[1], threshold=0.6)
                    distance_ = hamming_distance(listFingerTemplate[0], listFingerTemplate[1], threshold=91)
                    similarity_two = cv2.matchTemplate(np.frombuffer(listFingerTemplate[0], dtype=np.uint8), np.frombuffer(listFingerTemplate[1], dtype=np.uint8), cv2.TM_CCOEFF_NORMED)
                    distance__ = distance.euclidean(np.frombuffer(listFingerTemplate[0], dtype=np.uint8), np.frombuffer(listFingerTemplate[1], dtype=np.uint8))
                    distance___ = compare_templates(np.frombuffer(listFingerTemplate[0], dtype=np.uint8), np.frombuffer(listFingerTemplate[1], dtype=np.uint8))
                    confidence = cross_correlation(listFingerTemplate[0], listFingerTemplate[1], threshold=91)
                    print(f"Tỉ lệ trùng khớp với phương pháp jaccard: {jaccard_score}")
                    print(f"Tỉ lệ trùng với phương pháp cosine similarity: {ret} - {similarity}")
                    print(f"Tỉ lệ trùng với thuật toán Minutiae-based Matching: {match_score}")
                    print(f"Tỉ lệ trùng với thuật toán hamming distance: {distance_}")
                    print(f"Tỉ lệ trùng với cv2.matchTemplate: {similarity_two}")
                    print(f"Tỉ lệ trùng với euclid: {distance__}")
                    print(f"Tỉ lệ tương đồng: {distance___:.2f}%")
                    print(f"Tỉ lệ tương đồng với thuật toán Cross-Correlation: {confidence}%")
                    print(isinstance(listFingerTemplate[0], bytes))

            yesorno = input("-> Sent command (y/n): ")
            if yesorno.lower() == 'y':
                uart.send_command("GET_FINGERPRINT1")


        finally:
            # Đóng kết nối UART
            # uart.close()
            pass
