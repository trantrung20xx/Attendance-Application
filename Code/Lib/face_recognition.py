import cv2
import sys
import os
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from Lib import employee_management, face_training

# Đường dẫn đến model đã được training trước
yml_file_path = face_training.yml_file_path

# Tải font chữ hỗ trợ tiếng Việt
try:
    font = ImageFont.truetype(r"E:\University\Semester1_Year3\DOAN\App\Code\font\Arial.ttf", 20)
except IOError:
    font = ImageFont.load_default()

def initialize_recognizer(yml_path):
    """Khởi tạo bộ nhận diện khuôn mặt từ file .yml đã training."""
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=16, grid_x=8, grid_y=8)
    recognizer.read(yml_path)
    return recognizer

def initialize_face_cascade():
    """Khởi tạo bộ phát hiện khuôn mặt Haar Cascade."""
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def initialize_camera(width, height):
    """Khởi tạo camera và đặt kích thước."""
    webcam = cv2.VideoCapture(0)
    if not webcam.isOpened():
        print("Error opening camera!")
        sys.exit()
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, width)  # Chiều rộng
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  # Chiều cao
    return webcam

def initialize_clahe(clip_limit=2.0, tile_grid_size=(8, 8)):
    """Khởi tạo đối tượng CLAHE để cải thiện độ tương phản."""
    # Khởi tạo CLAHE giúp cải thiện độ tương phản của ảnh.
    # clipLimit giúp giới hạn độ tương phản tối đa
    # tileGridSize là kích thước vùng nhỏ (tile) để áp dụng Histogram Equalization
    return cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

def preprocess_frame(img, clahe):
    """
    Xử lý hình ảnh trước khi nhận diện.
    - Chuyển đổi sang ảnh grayscale.
    - Áp dụng CLAHE để tăng cường chất lượng ảnh.
    """
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_img = clahe.apply(gray_img)
    return enhanced_img

def detect_faces(img, face_cascade, min_width, min_height):
    """
    Phát hiện các khuôn mặt trong img.
    """
    return face_cascade.detectMultiScale(
        img,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(int(min_width), int(min_height))
    )

def draw_face_info(img, x, y, w, h, name, color, font):
    """ Vẽ thông tin khuôn mặt lên img. """
    # confidence_text = f" {round(100 - confidence)}%"
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

    # Chuyển đổi ảnh OpenCV (NumPy) sang định dạng PIL
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # Tạo đối tượng vẽ từ PIL
    draw = ImageDraw.Draw(img_pil)

    # Vẽ văn bản Unicode
    draw.text((x + 7, y - 28), name, font=font, fill=(127, 127, 255))

    # Chuyển đổi ảnh PIL trở lại OpenCV
    img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # cv2.putText(img, str(name), (x + 7, y - 10), font, 1, (255, 127, 127), 1)
    # cv2.putText(img, str(f"{confidence_text}%"), (x + 7, y + h - 10), font, 1, (255, 255, 0), 1)

def recognize_faces_live(webcam, recognizer, face_cascade, clahe, employee_list):
    """Hàm chính thực hiện nhận diện khuôn mặt."""
    minWidth = 0.080 * webcam.get(3)
    minHeight = 0.080 * webcam.get(4)

    # Đọc hình ảnh từ camera
    _, img = webcam.read()
    img = cv2.flip(img, 1)  # Lật hình ảnh theo chiều ngang
    gray_img = preprocess_frame(img, clahe)  # Xử lý ảnh

    # Phát hiện khuôn mặt
    faces = detect_faces(gray_img, face_cascade, minWidth, minHeight)

    for (x, y, w, h) in faces:
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Vẽ hình vuông quanh khuôn mặt
        id, confidence = recognizer.predict(gray_img[y:y+h, x:x+w]) # Nhận diện khuôn mặt
        # Kiểm tra độ tin cậy và lấy tên
        name = "Unknown"
        for employee in employee_list:
            if employee.face_id == id and confidence < 70:
                name = employee.name
                break
        color = (255, 0, 0) if name != "Unknown" else (0, 0, 255)
        # Vẽ hình vuông quanh khuôn mặt và hiển thị tên
        draw_face_info(img, x, y, w, h, name, color, font)

    return img  # Trả về hình ảnh đã nhận diện khuôn mặt

def main():
    print('\n[INFO] THE PROGRAM IS INITIALIZING. PLEASE WAIT A FEW SECONDS...')
    recognizer = initialize_recognizer(yml_file)
    face_cascade = initialize_face_cascade()
    webcam = initialize_camera(width=640, height=480)
    clahe = initialize_clahe()
    print('\n[INFO] INITIALIZATION SUCCESSFUL')

    employee_list = employee_management.EmployeeManagement.fetch_all_employees()  # Danh sách nhân viên từ cơ sở dữ liệu
    recognize_faces_live(webcam, recognizer, face_cascade, clahe, employee_list)

    print('[INFO] PROGRAM ENDED')
    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
