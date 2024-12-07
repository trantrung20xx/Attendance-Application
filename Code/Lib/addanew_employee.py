import os
import shutil
import time
import tkinter as tk
from tkinter.ttk import Frame, Label, Entry, Button, Style
import threading
from Lib.odbemployee import ODBEmployee
from Lib.employee_management import EmployeeManagement
from Lib import face_dataset, face_training
from Lib.attendance_live_tab import face_cascade, video, clahe
from Lib import attendance_live_tab

hasAuthenticated = False
flag_hasFaceID = False
def create_add_employee_tab(notebook, send_command_to_esp32, esp32_status_callback, width, height):
    # Tạo tab Thêm nhân viên mới
    add_employee_tab = Frame(notebook, style="TFrame", width=width, height=height)

    # Tiêu đề chính
    title = Label(
        add_employee_tab, text="Thêm Nhân Viên Mới",
        font=("Arial", 20, "bold"), anchor="center"
    )
    title.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")

    # Khung thông tin cơ bản
    basic_info_frame = Frame(add_employee_tab, padding=10, style="TFrame")
    basic_info_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    Label(basic_info_frame, text="Thông tin cơ bản", font=("Arial", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10
    )
    Label(basic_info_frame, text="Họ và tên:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    name_entry = Entry(basic_info_frame, font=("Arial", 12), width=30)
    name_entry.grid(row=1, column=1, padx=10, pady=5)

    Label(basic_info_frame, text="Phòng ban:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    department_entry = Entry(basic_info_frame, font=("Arial", 12), width=30)
    department_entry.grid(row=2, column=1, padx=10, pady=5)

    # Khung thêm dữ liệu
    data_entry_frame = Frame(add_employee_tab, padding=10, style="TFrame")
    data_entry_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

    Label(data_entry_frame, text="Thêm dữ liệu sinh trắc học", font=("Arial", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10
    )

    # Nút trạng thái và hành động
    def create_status_row(frame, row, label_text, command, status_label_text):
        Label(frame, text=label_text, font=("Arial", 12)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        status_label = Label(frame, text=status_label_text, font=("Arial", 12), foreground="red")
        status_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        action_button = Button(
            frame, text="Gửi lệnh", command=command, style="TButton"
        )
        action_button.grid(row=row, column=2, padx=10, pady=5)

        return status_label

    # Hàm thêm khuôn mặt mới
    def add_face():
        def start_face_capture():
            global hasAuthenticated, flag_hasFaceID, base_path
            name = name_entry.get().strip()
            department = department_entry.get().strip()

            if not name: # Nếu tên để trống
                message_label.config(text="Vui lòng nhập tên trước khi thêm khuôn mặt", foreground="red")
                return
            if not department: # Nếu phòng ban để trống
                message_label.config(text="Vui lòng nhập phòng ban trước khi thêm khuôn mặt", foreground="red")
                return
            if not flag_hasFaceID:
                try:
                    face_id = ODBEmployee.get_current_id()
                    employee_id = f"EMP{face_id:05d}"
                    save_dir = face_dataset.create_save_directory(face_training.base_path, name + "_" + employee_id)
                    face_dataset.capture_face_data(video, face_cascade, save_dir, face_id, clahe)
                    hasAuthenticated = True # Đã có phương thức xác thực cho nhân viên đang thêm mới
                    flag_hasFaceID = True # Đã thêm khuôn mặt cho id nhân viên đang tạo mới
                    face_status.config(text="Đã thêm", foreground="green")
                except Exception as e:
                    message_label.config(text=f"Lỗi khi thêm khuôn mặt: {str(e)}", foreground="red")
                    flag_hasFaceID = False
                    flag_hasFaceID = False
            else:
                message_label.config(text=f"Bạn đã thêm khuôn mặt rồi!", foreground="red")
        # Khởi chạy trong luồng mới
        threading.Thread(target=start_face_capture, daemon=True).start()

    # Hàm gửi lệnh
    def send_and_wait(command, status_label, success_text):
        def wait_for_response():
            send_command_to_esp32(command)
            while True:
                if esp32_status_callback(command):
                    status_label.config(text=success_text, foreground="green")
                    break
            time.sleep(0.5) # Đợi phản hồi từ ESP32

        threading.Thread(target=wait_for_response, daemon=True).start()

    # Các thành phần cho sinh trắc học
    face_status = create_status_row(
        data_entry_frame, 1, "Khuôn mặt:",
        add_face,
        "Chưa thêm"
    )
    fingerprint1_status = create_status_row(
        data_entry_frame, 2, "Vân tay 1:",
        lambda: send_and_wait("ADD_FINGERPRINT1", fingerprint1_status, "Đã thêm vân tay 1"),
        "Chưa thêm"
    )
    fingerprint2_status = create_status_row(
        data_entry_frame, 3, "Vân tay 2:",
        lambda: send_and_wait("ADD_FINGERPRINT2", fingerprint2_status, "Đã thêm vân tay 2"),
        "Chưa thêm"
    )
    rfid_status = create_status_row(
        data_entry_frame, 4, "RFID:",
        lambda: send_and_wait("ADD_RFID", rfid_status, "Đã thêm RFID"),
        "Chưa thêm"
    )

    # Thông báo
    message_label = Label(add_employee_tab, text="", font=("Arial", 12), foreground="red")
    message_label.grid(row=3, column=0, columnspan=2, pady=(10, 20))

    def save_employee():
        global hasAuthenticated, flag_hasFaceID
        name = name_entry.get().strip()
        department = department_entry.get().strip()
        if not name: # Nếu tên đang được để trống
            message_label.config(text="Tên không được để trống!", foreground="red")
            return
        if not department: # Nếu phòng ban đang được để trống
            message_label.config(text="Phòng ban không được để trống!", foreground="red")
            return
        if not hasAuthenticated: # Nếu chưa có phương thức xác thực nào
            message_label.config(text="Phải có ít nhất một phương thức xác thực!", foreground="red")
            return

        def perform_training():
            try:
                face_training.train_and_save_model(face_training.base_path, face_training.yml_file_path)
                add_employee_tab.after(0, lambda: message_label.config(text="Thêm nhân viên thành công!", foreground="green"))
                attendance_live_tab.is_recognizer_initialized = True
            except Exception as e:
                print(f"Lỗi trong perform_training: {str(e)}")
                add_employee_tab.after(0, lambda: message_label.config(text=f"Lỗi training: {str(e)}", foreground="red"))
            finally:
                # Tự động xóa thông báo sau 5 giây
                add_employee_tab.after(5000, lambda: message_label.config(text=""))

        try:
            # Tạo nhân viên mới và lưu vào cơ sở dữ liệu
            new_employee = EmployeeManagement.create_employee(
                name=name,
                department=department
            )
            if flag_hasFaceID: # Nếu có khuôn mặt mới thêm vào
                message_label.config(text="Đang thêm nhân viên mới xin chờ...", foreground="orange")
                # Training mô hình và lưu models
                threading.Thread(target=perform_training, daemon=True).start()
            name_entry.delete(0, tk.END) # Làm trống ô nhập liệu
            department_entry.delete(0, tk.END) # Làm trống ô nhập liệu
            flag_hasFaceID = False
        except Exception as e:
            message_label.config(text=f"Thêm nhân viên thất bại: {str(e)}", foreground="red")
            shutil.rmtree(os.path.join(face_training.base_path, name))
            threading.Thread(target=lambda: face_training.train_and_save_model(face_training.base_path, face_training.yml_file_path), daemon=True).start()
        finally:
            face_status.config(text="Chưa thêm", foreground="red")
            hasAuthenticated = False # Reset trạng thái xác thực

    # Nút lưu
    style = Style()
    style.configure("Custom.TButton", font=("Arial", 12))  # Định nghĩa font cho kiểu `Custom.TButton`
    save_button = Button(
        add_employee_tab, text="Lưu Nhân Viên",
        command=save_employee, style="Custom.TButton",
        padding=[15, 7]
    )
    save_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Tùy chỉnh khung lưới
    add_employee_tab.grid_columnconfigure(0, weight=1)
    add_employee_tab.grid_columnconfigure(1, weight=1)

    return add_employee_tab
