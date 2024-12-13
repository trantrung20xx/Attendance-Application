import tkinter
from tkinter import ttk
from Lib.odbemployee import cursor
from datetime import datetime

def fetch_attendance_logs():
    """
    Lấy danh sách điểm danh từ cơ sở dữ liệu.
    """
    cursor.execute("""
        SELECT
            al.EmployeeID,
            e.Name_,
            e.Department,
            al.CheckInTime,
            al.Status_1,
            al.CheckOutTime,
            al.Status_2
        FROM AttendanceLogs al
        JOIN Employees e ON al.EmployeeID = e.EmployeeID
        ORDER BY al.CheckInTime DESC
    """)
    return cursor.fetchall()

def format_row(row):
    """
    Định dạng từng hàng dữ liệu trước khi đưa vào bảng.
    """
    return [
        row[0],  # EmployeeID
        row[1],  # Name
        row[2],  # Department
        row[3].strftime('%Y-%m-%d - %H:%M:%S') if isinstance(row[3], datetime) else row[3],
        row[4],  # Status1
        row[5].strftime('%Y-%m-%d - %H:%M:%S') if isinstance(row[5], datetime) else row[5],
        row[6],  # Status2
    ]

def update_attendance_table(treeview, data):
    """
    Cập nhật dữ liệu mới vào Treeview.
    """
    # Xóa dữ liệu cũ
    for row in treeview.get_children():
        treeview.delete(row)

    # Thêm dữ liệu mới
    for record in data:
        formatted_record = format_row(record)
        treeview.insert("", "end", values=formatted_record)

def refresh_attendance_table(treeview):
    """
    Làm mới bảng dữ liệu tự động sau mỗi 5 giây.
    """
    data = fetch_attendance_logs()  # Lấy dữ liệu từ cơ sở dữ liệu
    update_attendance_table(treeview, data)
    treeview.after(5000, lambda: refresh_attendance_table(treeview))  # Lặp lại sau 5 giây

def create_attendance_list_tab(parent, width=1000, height=500):
    """
    Tạo tab hiển thị danh sách điểm danh.
    """
    tab = tkinter.Frame(parent, bg="lightgreen", width=width, height=height)

    # Tiêu đề
    tkinter.Label(tab, text="Danh sách điểm danh", font=("Arial", 20), bg="lightgreen").pack(pady=10)

    # Cấu hình bảng Treeview
    columns = ("EmployeeID", "Name", "Department", "CheckInTime", "Status1", "CheckOutTime", "Status2")
    tree = ttk.Treeview(tab, columns=columns, show="headings")

    # Đặt tiêu đề và định dạng các cột
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

    tree.pack(expand=True, fill="both")

    # Bắt đầu làm mới tự động
    refresh_attendance_table(tree)

    return tab
