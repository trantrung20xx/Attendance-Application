import cv2
import numpy as np
from PIL import Image
import os

base_path = os.path.dirname(os.path.abspath(__file__)) # Thư mục chứa file hiện tại
# Lùi lại 2 cấp
for _ in range(1):
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
        for dirname in _:
            pathname = os.path.join(root,dirname)
            print(pathname)
            pathname = os.path.split(pathname)[-1].split('_')
            print(pathname[0], pathname[1])
    return lst_face_data

get_face_data(base_path)
