import os
import tkinter
from tkinter.ttk import *
from tkinter import messagebox
import cv2
import PIL.Image, PIL.ImageTk
from threading import Thread
from Lib import face_recognition, face_dataset, face_training, employee_management

def initialize_video_components(width, height):
    try:
        if not os.path.exists(face_recognition.yml_file_path):
            return None, face_recognition.initialize_face_cascade(),\
                face_recognition.initialize_camera(width=width, height=height),\
                face_recognition.initialize_clahe()

        # Nhận diện khuôn mặt (điểm danh)
        recognizer = face_recognition.initialize_recognizer(face_recognition.yml_file_path)
        face_cascade = face_recognition.initialize_face_cascade()
        video = face_recognition.initialize_camera(width=width, height=height)
        clahe = face_recognition.initialize_clahe()  # Khởi tạo CLAHE
        return recognizer, face_cascade, video, clahe
    except Exception as e:
        print(f"[ERROR] Failed to initialize video components: {e}")
        return None, None, None, None

# Khởi tạo các thành phần liên quan đến video
recognizer, face_cascade, video, clahe = initialize_video_components(width=520, height=480)
is_recognizer_initialized = False
def create_video_frame(parent_frame, width, height):
    """Tạo frame để hiển thị video."""
    video_frame = tkinter.Frame(parent_frame)
    video_frame.pack(anchor=tkinter.NW)
    canvas = tkinter.Canvas(video_frame, width=width, height=height)
    canvas.pack()
    return canvas

def update_frame(canvas, photo_container, running, parent_window):
    """Hàm cập nhật khung hình video."""
    if not running[0]:
        return

    global recognizer, face_cascade, video, clahe, init_count

    if recognizer:
        # Lấy danh sách nhân viên từ cơ sở dữ liệu
        employee_list = employee_management.EmployeeManagement.fetch_all_employees()
        # Nhận diện khuôn mặt (điểm danh)
        img = face_recognition.recognize_faces_live(video, recognizer, face_cascade, clahe, employee_list)
    else:
        # Đọc khung hình từ camera
        if video is not None:
            _, img = video.read() # Chỉ hiển thị khung hình từ camera nếu không có mô hình
            img = cv2.flip(img, 1) # Lật hình ảnh theo chiều ngang

    # img = cv2.resize(img, dsize=None, fx=1, fy=1) # resize kích thước của ảnh hiển thị
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Chuyển hệ màu
    img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img)) # Chuyển ảnh từ array sang tkinter image và vẽ lên canvas
    photo_container[0] = img  # Cập nhật ảnh mới vào container
    canvas.create_image(0, 0, image=img, anchor=tkinter.NW) # Vẽ ảnh vào canvas hiển thị lên màn hình

    # Sau 15ms thì chạy lại lệnh update_frame
    parent_window.after(15, lambda: update_frame(canvas, photo_container, running, parent_window))

def create_attendance_live_tab(parent_window, width, height):
    attendance_frame = tkinter.Frame(parent_window, bg='lightblue', width=width, height=height)
    attendance_frame.pack()

    # Khởi tạo các thành phần liên quan đến video
    # recognizer, face_cascade, video, clahe = initialize_video_components(width=520, height=480)
    # Lấy độ phân giải của video
    # canvas_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # canvas_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    canvas_width = 520
    canvas_height = 480

    # Tạo frame video và canvas
    canvas = create_video_frame(attendance_frame, canvas_width, canvas_height)

    # Quản lý trạng thái chạy
    photo_container = [None]
    running = [False]

    def start_recognition():
        global recognizer
        """Bắt đầu nhận diện khuôn mặt."""
        if is_recognizer_initialized:
            recognizer = face_recognition.initialize_recognizer(face_recognition.yml_file_path)
        if recognizer is None:
            messagebox.showwarning("Warning", "Chưa có dữ liệu nhận diện khuôn mặt. Vui lòng thêm dữ liệu!")

        if not running[0]:
            running[0] = True
            update_frame(canvas, photo_container, running, parent_window)

    def stop_recognition():
        """Dừng nhận diện khuôn mặt."""
        running[0] = False

    return attendance_frame, start_recognition, stop_recognition
