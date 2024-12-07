import cv2
import numpy as np
from PIL import Image
import os

base_path = os.path.dirname(os.path.abspath(__file__)) # Thư mục chứa file hiện tại
# Lùi lại 2 cấp
for _ in range(2):
    base_path = os.path.dirname(base_path)

# Đường dẫn đến Models/trainer.yml
yml_file_path = os.path.join(base_path, "Models")
if not os.path.exists(yml_file_path): # Tạo đường dẫn đến thư mục Models nếu chưa tồn tại
    os.makedirs(yml_file_path)
# Tạo file trainer.yml trong thư mục Models
yml_file_path = os.path.join(yml_file_path, "trainer.yml")

# Đường dẫn đến DataSet/FaceData/processed
base_path = os.path.join(base_path, "DataSet", "FaceData", "processed")
if not os.path.exists(base_path): # Tạo đường dẫn nếu chưa tồn tại
    os.makedirs(base_path)

def get_face_data(path):
    """
    Lấy tất cả các đường dẫn tới file ảnh khuôn mặt từ thư mục chỉ định.

    Args:
        path (str): Đường dẫn thư mục chứa dữ liệu khuôn mặt.

    Returns:
        list: Danh sách đường dẫn tới các file ảnh khuôn mặt.
    """
    lst_face_data = []
    for root, _, files in os.walk(path):
        for filename in files:
            face_data = os.path.join(root, filename)
            lst_face_data.append(face_data)
    return lst_face_data

# Tạo mô hình nhận diện khuôn mặt
def initialize_recognizer():
    """
    Khởi tạo mô hình nhận diện khuôn mặt LBPH.

    Returns:
        cv2.face_LBPHFaceRecognizer: Mô hình nhận diện khuôn mặt.
    """
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        print('[INFO] Successfully initialized face recognition model.')
        return recognizer
    except AttributeError:
        raise ImportError('cv2.face is not available. Please install OpenCV with cv2.face module.')

# Tải hình ảnh và label từ thư mục
def get_images_and_labels(path):
    """
    Lấy dữ liệu ảnh khuôn mặt và ID từ thư mục.

    Args:
        path (str): Đường dẫn tới thư mục chứa ảnh.

    Returns:
        tuple: (face_samples, ids)
            - face_samples: Danh sách ảnh khuôn mặt đã chuyển sang ảnh xám.
            - ids: Danh sách ID tương ứng với các ảnh khuôn mặt.
    """
    lst_face_data = get_face_data(path)
    face_samples = []
    ids = []
    for face_img_path in lst_face_data:
        gray_image = cv2.imread(face_img_path, cv2.IMREAD_GRAYSCALE)
        if gray_image is not None:
            id = int(os.path.split(face_img_path)[-1].split(".")[0])  # Lấy ID từ tên file
            face_samples.append(gray_image)
            ids.append(id)
    return face_samples, ids

def train_and_save_model(base_path, model_path):
    """
    Huấn luyện mô hình nhận diện khuôn mặt và lưu vào file.

    Args:
        base_path (str): Đường dẫn thư mục chứa dữ liệu khuôn mặt.
        model_path (str): Đường dẫn lưu trữ mô hình nhận diện đã được huấn luyện.
    """
    recognizer = initialize_recognizer()
    faces, ids = get_images_and_labels(base_path)

    print('\n[INFO] Training faces data. It will take a few seconds to train. Wait...')
    recognizer.train(faces, np.array(ids))  # Huấn luyện mô hình

    recognizer.write(model_path)  # Lưu mô hình
    print('\n[INFO] {0} faces trained.'.format(len(np.unique(ids))))

if __name__ == '__main__':
    train_and_save_model(base_path, yml_file_path)
