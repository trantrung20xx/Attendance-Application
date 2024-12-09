import os
import shutil
import tkinter as tk
from tkinter.ttk import *
from Lib.employee_management import EmployeeManagement
from Lib import face_training
import threading
from Lib.employee_edit_window import EmployeeEditWindow
from Lib import attendance_live_tab

# from employee_management import EmployeeManagement

def create_employee_management_tab(notebook, width, height):
    """
    Tạo tab 'Quản lý nhân viên' hiển thị danh sách nhân viên.
    """
    # Frame chính của tab 'Quản lý nhân viên'
    employee_management_tab = tk.Frame(notebook, bg="lightyellow", width=width, height=height)

    # Tiêu đề
    Label(
        employee_management_tab,
        text="Danh sách nhân viên",
        font=("Arial", 20),
        background="lightyellow"
    ).pack(pady=10)

    # Frame cho bảng danh sách
    list_frame = Frame(employee_management_tab)
    list_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Định nghĩa kiểu (Style) cho bảng
    style = Style()
    style.configure("Treeview", font=("Arial", 12), rowheight=30)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f0f0f0", foreground="grey")
    style.map(
        "Treeview",
        background=[("selected", "#6baed6")],  # Màu nền khi được chọn
        foreground=[("selected", "white")],  # Màu chữ khi được chọn
    )

    # Tạo bảng hiển thị danh sách nhân viên
    tree = Treeview(list_frame, columns=("No.", "ID", "Name", "Department", "Actions"), show="headings", height=15)
    tree.heading("No.", text="STT")
    tree.heading("ID", text="Mã nhân viên")
    tree.heading("Name", text="Họ và tên")
    tree.heading("Department", text="Phòng ban")
    tree.heading("Actions", text="Tùy chọn")

    tree.column("No.", width=70, anchor="center")
    tree.column("ID", width=150, anchor="center")
    tree.column("Name", width=250, anchor="w")
    tree.column("Department", width=200, anchor="center")
    tree.column("Actions", width=180, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Thanh cuộn dọc cho bảng
    scrollbar = Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # # Thêm các kiểu màu xen kẽ
    # style.configure("evenrow", background="#f9f9f9") # Hàng chẵn
    # style.configure("oddrow", background="#eaf3fa") # Hàng lẻ

    # Áp dụng các kiểu cho bảng
    tree.tag_configure("evenrow", background="#eaf3fa")
    tree.tag_configure("oddrow", background="#d7f9fa")

    # Hàm cập nhật danh sách nhân viên
    def update_employee_list():
        tree.delete(*tree.get_children()) # Xóa tất cả các dòng hiện tại
        # Lấy danh sách nhân viên mới từ cơ sở dữ liệu
        employee_list = EmployeeManagement.fetch_all_employees() # Dữ liệu mới
        if employee_list:
            attendance_live_tab.is_recognizer_initialized = False
        for index, employee in enumerate(employee_list):
            # Thêm nhân viên vào cuối bảng (thêm dòng mới)
            # Áp dụng màu sắc xen kẽ
            row_color = "evenrow" if index % 2 == 0 else "oddrow"
            tree.insert(
                "",
                "end",
                values=(index + 1, employee.employee_id, "  " + employee.name, employee.department, "Chỉnh sửa | Xóa"),
                tags=(row_color,))

    # Sự kiện khi nhấn vào một dòng trong bảng
    def handle_action(event):
        selected_item = tree.selection()
        # print(f"Nhấn chuột tại ({event.x}, {event.y})")
        if not selected_item:
            return  # Không có nhân viên nào được chọn

        column = tree.identify_column(event.x) # Xác định cột được nhấn
        selected_employee = tree.item(selected_item, "values")
        employee_id = selected_employee[1] # Lấy id của nhân viên được chọn
        name = selected_employee[2].strip() # Lấy tên của nhân viên

        if column == "#5": # Cột Tùy chọn
            # action = event.widget.item(selected_item)["values"][-1] <=> selected_employee[-1]
            x_offset = event.x
            if 710 <= x_offset <= 781: # Nhấn vào Chỉnh sửa
                open_edit_window(employee_id)
            elif 793 <= x_offset <= 825: # Nhấn vào Xóa
                delete_employee(employee_id, name)

    # Nút chỉnh sửa thông tin nhân viên
    def open_edit_window(employee_id):
        employee = EmployeeManagement.find_employee(employee_id)
        # Kiểm tra có nhân viên có trong cơ sở dữ liệu không
        if employee is None: # Nếu nhân viên không có trong cơ sở dữ liệu
            return
        # Mở cửa sổ chỉnh sửa
        EmployeeEditWindow(employee_management_tab, employee, update_employee_list)

    # Hàm xóa nhân viên
    def delete_employee(employee_id, name):
        # Hiện thông báo xác nhận xóa nhân viên
        confirmation = tk.messagebox.askyesno(
            title="Xác nhận xóa",
            message=f"Nhân viên:  {name}\nMã nhân viên:  {employee_id}\n\nBạn có chắc muốn xóa nhân viên này không?"
        )
        if confirmation:
            # Xóa thư mục chứa ảnh của nhân viên cần xóa
            for root, dirname, files in os.walk(face_training.base_path):
                for path_face_data in dirname:
                    path_face_data = os.path.join(root, path_face_data) # Đường dẫn đến folder chứa ảnh của nhân viên cần xóa
                    face_data = os.path.split(path_face_data)[-1] # Lấy ra tên folder chứa ảnh của nhân viên cần xóa
                    if face_data == employee_id:
                        shutil.rmtree(path_face_data)
                        break

            EmployeeManagement.delete_employee(employee_id) # Thực hiện xóa từ cơ sở dữ liệu

            # Training lại mô hình sau khi xóa nhân viên
            threading.Thread(target=lambda: face_training.train_and_save_model(face_training.base_path, face_training.yml_file_path), daemon=True).start()
            update_employee_list() # Cập nhật lại danh sách sau khi xóa

    # Gắn sự kiện nhấn và nhả chuột vào bảng
    tree.bind("<ButtonRelease-1>", handle_action)

    # Tải dữ liệu ban đầu
    update_employee_list()

    return employee_management_tab, update_employee_list
