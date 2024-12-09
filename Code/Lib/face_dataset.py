import cv2
import os
from Lib import face_recognition
# import face_recognition

def capture_frame(video):
    ret, frame = video.read()  # Đọc khung hình
    if not ret:
        print("[ERROR] Lỗi khi đọc từ webcam.")
        return None
    frame = cv2.flip(frame, 1)  # Lật ngang hình ảnh
    return frame

def create_save_directory(base_path, face_data):
    """
    Tạo thư mục lưu trữ dữ liệu khuôn mặt.
    - base_path: đường dẫn gốc.
    - face_data: Tên folder lưu dữ liệu khuôn mặt.
    """
    save_dir = os.path.join(base_path, face_data)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return save_dir

def save_face(face_region, save_dir, face_id, count):
    """
    Lưu ảnh khuôn mặt vào thư mục đã chỉ định.
    - face_region: khuôn mặt được cắt từ ảnh.
    - save_dir: thư mục lưu trữ.
    - face_id: ID của khuôn mặt.
    - count: số thứ tự của ảnh.
    """
    file_path = os.path.join(save_dir, f'{face_id}.{count}.jpg')
    cv2.imwrite(file_path, face_region)

def capture_face_data(webcam, face_detector, save_dir, face_id, clahe, max_count=200):
    """Chụp và lưu dữ liệu khuôn mặt."""
    count = 0
    print('\nĐang khởi tạo hình ảnh. Vui lòng nhìn vào camera:')

    while count < max_count:
        frame = capture_frame(webcam)  # Đọc khung hình
        gray_img = face_recognition.preprocess_frame(frame, clahe) # Đổi sang ảnh grey và tăng độ tương phản

        # Phát hiện các khuôn mặt trong frame
        faces = face_detector.detectMultiScale(
            gray_img, scaleFactor=1.3, minNeighbors=5
        )

        for (x, y, w, h) in faces:
            count += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Vẽ hình chữ nhật quanh khuôn mặt
            face_crop = gray_img[y: y + h, x: x + w]  # Cắt vùng khuôn mặt
            save_face(face_crop, save_dir, face_id, count)  # Lưu khuôn mặt

        cv2.imshow('Get Face Data', frame)  # Hiển thị ảnh

        # Điều kiện thoát
        if cv2.waitKey(1) & 0xFF == 27:  # Nhấn ESC để thoát
            break
    cv2.destroyAllWindows()
    print('\n[INFO] Hoàn thành. Đã lưu dữ liệu khuôn mặt')

def main():
    # Khởi tạo camera
    webcam = face_recognition.initialize_camera()
    # Khởi tạo bộ phát hiện khuôn mặt
    face_detector = face_recognition.initialize_face_cascade()
    # Khởi tạo CLAHE
    clahe = face_recognition.initialize_clahe()
    # Lấy thông tin người dùng
    face_name = input('\nNhập face name: ')
    face_id = input('\nNhập face id: ')
    # Tạo thư mục lưu trữ
    base_path = 'E:\\University\\Semester1_Year3\\DOAN\\App\\DataSet\\FaceData\\Processed'
    save_dir = create_save_directory(base_path, face_name)
    # Bắt đầu chụp dữ liệu khuôn mặt
    capture_face_data(webcam, face_detector, save_dir, face_id, clahe)
    # Giải phóng tài nguyên
    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
   main()



