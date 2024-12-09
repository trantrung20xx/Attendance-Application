import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
import threading
from Lib.employee_management import EmployeeManagement
from Lib import face_dataset, face_training
from Lib import attendance_live_tab
from Lib.attendance_live_tab import face_cascade, video, clahe

# Biến ghi nhận thay đổi dữ liệu của khuôn mặt
has_changed = [False]

class EmployeeEditWindow:
    def __init__(self, root, employee, update_employee_list):
        self.root = root
        self.employee = employee
        self.update_employee_list = update_employee_list

        self.window = tk.Toplevel(self.root)
        self.window.title(f"Chỉnh sửa nhân viên mã: {employee.employee_id}")
        self.window.geometry("800x350")

        # Cấu hình grid cho cửa sổ chính
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        # Khung thông tin cơ bản
        self.basic_info_frame = tk.LabelFrame(self.window, text="Thông tin cơ bản", font=("Arial", 14, "bold"), padx=10, pady=10)
        self.basic_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Họ và tên
        self.name_label = tk.Label(self.basic_info_frame, text="Họ và tên:", font=("Arial", 12))
        self.name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 3))
        self.name_entry = tk.Entry(self.basic_info_frame, font=("Arial", 12), width=30)
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(3, 10))

         # Phòng ban
        self.department_label = tk.Label(self.basic_info_frame, text="Phòng ban:", font=("Arial", 12))
        self.department_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 3))
        self.department_entry = tk.Entry(self.basic_info_frame, font=("Arial", 12), width=30)
        self.department_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=3)

        # Khung dữ liệu sinh trắc học
        self.biometric_info_frame = tk.LabelFrame(self.window, text="Thêm dữ liệu sinh trắc học", font=("Arial", 14, "bold"), padx=10, pady=10)
        self.biometric_info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Khuôn mặt
        self.face_label = tk.Label(self.biometric_info_frame, text="Khuôn mặt:", font=("Arial", 12))
        self.face_label.grid(row=0, column=0, sticky="w", padx=10)
        self.face_status = tk.Label(self.biometric_info_frame, text="Chưa thêm", fg="red", font=("Arial", 12))
        self.face_status.grid(row=0, column=1, sticky="w", padx=10)
        self.add_face_button = tk.Button(self.biometric_info_frame, text="Thêm mới", command=self.add_face, font=("Arial", 12))
        self.add_face_button.grid(row=0, column=2, padx=5)
        self.remove_face_button = tk.Button(self.biometric_info_frame, text="Xóa", command=self.remove_face, state="disabled", font=("Arial", 12))
        self.remove_face_button.grid(row=0, column=3, padx=5)

        # Vân tay 1
        self.fingerprint1_label = tk.Label(self.biometric_info_frame, text="Vân tay 1:", font=("Arial", 12))
        self.fingerprint1_label.grid(row=1, column=0, sticky="w", padx=10)
        self.fingerprint1_status = tk.Label(self.biometric_info_frame, text="Chưa thêm", fg="red", font=("Arial", 12))
        self.fingerprint1_status.grid(row=1, column=1, sticky="w", padx=10)
        self.add_fingerprint1_button = tk.Button(self.biometric_info_frame, text="Thêm mới", command=self.add_fingerprint1, font=("Arial", 12))
        self.add_fingerprint1_button.grid(row=1, column=2, padx=5)
        self.remove_fingerprint1_button = tk.Button(self.biometric_info_frame, text="Xóa", command=self.remove_fingerprint1, state="disabled", font=("Arial", 12))
        self.remove_fingerprint1_button.grid(row=1, column=3, padx=5)

         # Vân tay 2
        self.fingerprint2_label = tk.Label(self.biometric_info_frame, text="Vân tay 2:", font=("Arial", 12))
        self.fingerprint2_label.grid(row=2, column=0, sticky="w", padx=10)
        self.fingerprint2_status = tk.Label(self.biometric_info_frame, text="Chưa thêm", fg="red", font=("Arial", 12))
        self.fingerprint2_status.grid(row=2, column=1, sticky="w", padx=10)
        self.add_fingerprint2_button = tk.Button(self.biometric_info_frame, text="Thêm mới", command=self.add_fingerprint2, font=("Arial", 12))
        self.add_fingerprint2_button.grid(row=2, column=2, padx=5)
        self.remove_fingerprint2_button = tk.Button(self.biometric_info_frame, text="Xóa", command=self.remove_fingerprint2, state="disabled", font=("Arial", 12))
        self.remove_fingerprint2_button.grid(row=2, column=3, padx=5)

        # RFID
        self.rfid_label = tk.Label(self.biometric_info_frame, text="RFID:", font=("Arial", 12))
        self.rfid_label.grid(row=3, column=0, sticky="w", padx=10)
        self.rfid_status = tk.Label(self.biometric_info_frame, text="Chưa thêm", fg="red", font=("Arial", 12))
        self.rfid_status.grid(row=3, column=1, sticky="w", padx=10)
        self.add_rfid_button = tk.Button(self.biometric_info_frame, text="Thêm mới", command=self.add_rfid, font=("Arial", 12))
        self.add_rfid_button.grid(row=3, column=2, padx=5)
        self.remove_rfid_button = tk.Button(self.biometric_info_frame, text="Xóa", command=self.remove_rfid, state="disabled", font=("Arial", 12))
        self.remove_rfid_button.grid(row=3, column=3, padx=5)

        # Nút lưu nhân viên
        self.save_button = tk.Button(self.window, text="Lưu Thay Đổi", command=self.save_employee, font=("Arial", 12))
        self.save_button.grid(row=1, column=0, columnspan=2, pady=20)

        # Thông báo
        self.message_label = tk.Label(self.window, text="", font=("Arial", 12), fg="red")
        self.message_label.grid(row=2, column=0, columnspan=2, pady=(10, 20))

        # Cấu hình để các ô grid trong cửa sổ này đều có thể tự động giãn nở
        self.basic_info_frame.grid_columnconfigure(0, weight=1)
        self.basic_info_frame.grid_columnconfigure(1, weight=1)
        self.biometric_info_frame.grid_columnconfigure(0, weight=1)
        self.biometric_info_frame.grid_columnconfigure(1, weight=1)
        self.biometric_info_frame.grid_columnconfigure(2, weight=1)
        self.biometric_info_frame.grid_columnconfigure(3, weight=1)

        # Tải dữ liệu nhân viên vào các trường nhập liệu
        self.load_employee_data()

    def load_employee_data(self):
        if self.employee:
            # Tải dữ liệu nhân viên vào các trường nhập liệu
            self.name_entry.insert(0, self.employee.name)
            self.department_entry.insert(0, self.employee.department)

            # Cập nhật trạng thái dữ liệu sinh trắc học
            self.update_biometric_status()

    def check_hasFaceID(self):
        # Hàm kiểm tra sự tồn tại của dữ liệu khuôn mặt của employee cần chỉnh sửa
        face_data = os.path.join(face_training.base_path, self.employee.employee_id)
        if os.path.exists(face_data): # Nếu đã có dữ liệu khuôn mặt
            return True
        else:
            return False
    def update_biometric_status(self):
        # Cập nhật tình trạng dữ liệu sinh trắc học
        if self.check_hasFaceID():
            self.face_status.config(text="Đã có", fg="green")
        if self.employee.fingerprint_data_1:
            self.fingerprint1_status.config(text="Đã có", fg="green")
        if self.employee.fingerprint_data_2:
            self.fingerprint2_status.config(text="Đã có", fg="green")
        if self.employee.rfid_data:
            self.rfid_status.config(text="Đã có", fg="green")

    def add_face(self):
        self.add_face_button.config(state="disabled")
        def start_face_capture():
            try:
                face_id = self.employee.face_id
                employee_id = self.employee.employee_id
                save_dir = face_dataset.create_save_directory(face_training.base_path, employee_id)
                face_dataset.capture_face_data(video, face_cascade, save_dir, face_id, clahe)

                self.face_status.config(text="Đã có", fg="green")
                self.remove_face_button.config(state="normal")
                has_changed[0] = True
            except Exception as e:
                self.add_face_button.config(state="normal")
                self.message_label.config(text=f"Lỗi khi thêm khuôn mặt: {str(e)}", fg="red")
                print(f"Lỗi khi thêm khuôn mặt: {str(e)}")

        # Khởi chạy trong luồng mới
        threading.Thread(target=start_face_capture, daemon=True).start()

    def remove_face(self):
        try:
            shutil.rmtree(os.path.join(face_training.base_path, self.employee.employee_id))
            threading.Thread(target=lambda: face_training.train_and_save_model(face_training.base_path, face_training.yml_file_path), daemon=True).start()

            self.face_status.config(text="Chưa thêm", fg="red")
            self.remove_face_button.config(state="disabled")
            self.add_face_button.config(state="normal")
        except Exception as e:
            messagebox.showinfo("Lỗi", f"Lỗi training: {str(e)}")

    def add_fingerprint1(self):
        self.fingerprint1_status.config(text="Đã có", fg="green")
        self.remove_fingerprint1_button.config(state="normal")
        self.add_fingerprint1_button.config(state="disabled")

    def remove_fingerprint1(self):
        self.fingerprint1_status.config(text="Chưa thêm", fg="red")
        self.remove_fingerprint1_button.config(state="disabled")
        self.add_fingerprint1_button.config(state="normal")

    def add_fingerprint2(self):
        self.fingerprint2_status.config(text="Đã có", fg="green")
        self.remove_fingerprint2_button.config(state="normal")
        self.add_fingerprint2_button.config(state="disabled")

    def remove_fingerprint2(self):
        self.fingerprint2_status.config(text="Chưa thêm", fg="red")
        self.remove_fingerprint2_button.config(state="disabled")
        self.add_fingerprint2_button.config(state="normal")

    def add_rfid(self):
        self.rfid_status.config(text="Đã có", fg="green")
        self.remove_rfid_button.config(state="normal")
        self.add_rfid_button.config(state="disabled")

    def remove_rfid(self):
        self.rfid_status.config(text="Chưa thêm", fg="red")
        self.remove_rfid_button.config(state="disabled")
        self.add_rfid_button.config(state="normal")

    def perform_training(self):
        try:
            face_training.train_and_save_model(face_training.base_path, face_training.yml_file_path)
            attendance_live_tab.is_recognizer_initialized = True
        except Exception as e:
            messagebox.showinfo("Lỗi", f"Lỗi training: {str(e)}")
            print(f"Lỗi trong perform_training: {str(e)}")

    def save_employee(self):
        new_name = self.name_entry.get().strip()
        new_department = self.department_entry.get().strip()

        if not new_name or not new_department:
            messagebox.showerror("Lỗi", "Họ tên và phòng ban không được để trống!")
            return

        updated = EmployeeManagement.update_employee(
            employee_id=self.employee.employee_id,
            name=new_name,
            fingerprint_data_1=self.employee.fingerprint_data_1,
            fingerprint_data_2=self.employee.fingerprint_data_2,
            rfid_data=self.employee.rfid_data,
            department=new_department
        )

        if updated:
            messagebox.showinfo("Thành công", "Cập nhật thông tin nhân viên thành công.")
            self.update_employee_list()  # Gọi hàm cập nhật danh sách
            if has_changed[0]: # Nếu dữ liệu khuôn mặt đã có thay đổi
                self.message_label.config(text="Đang thêm nhân viên mới xin chờ...", fg="orange")
                # Training và lưu mô hình
                threading.Thread(target=self.perform_training, daemon=True).start()
            self.window.destroy()
        else:
            messagebox.showerror("Lỗi", "Cập nhật thất bại.")
            if has_changed[0]: # Nếu dữ liệu khuôn mặt đã có thay đổi
                self.remove_face()
