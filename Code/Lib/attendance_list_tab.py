import tkinter
from tkinter import ttk
from Lib.odbemployee import cursor
from datetime import datetime

class AttendanceListApp:
    def __init__(self, parent, width=1000, height=500):
        """
        Khởi tạo giao diện cho tab Danh sách điểm danh
        """
        self.parent = parent
        self.width = width
        self.height = height

        self.tab = tkinter.Frame(self.parent, bg="lightgreen", width=self.width, height=self.height)
        self.tree = None
        self.create_widgets()

    def create_widgets(self):
        """
        Tạo các widget (như Label, Treeview) cho tab danh sách điểm danh.
        """
        # Tiêu đề
        tkinter.Label(self.tab, text="Danh sách điểm danh", font=("Arial", 20), bg="lightgreen").pack(pady=10)

        # Cấu hình bảng Treeview
        columns = ("EmployeeID", "Name", "Department", "CheckInTime", "Status1", "CheckOutTime", "Status2")
        self.tree = ttk.Treeview(self.tab, columns=columns, show="headings")

        # Đặt tiêu đề và định dạng các cột
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(expand=True, fill="both")

    def fetch_attendance_logs(self):
        """
        Lấy danh sách điểm danh từ cơ sở dữ liệu.
        """
        try:
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
        except Exception as e:
            print(f"Error fetching attendance logs: {e}")
            return []

    def format_row(self, row):
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

    def update_attendance_table(self, data):
        """
        Cập nhật dữ liệu mới vào Treeview.
        """
        # Xóa dữ liệu cũ
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Thêm dữ liệu mới
        for record in data:
            formatted_record = self.format_row(record)
            self.tree.insert("", "end", values=formatted_record)

    def refresh(self):
        """
        Làm mới bảng điểm danh với dữ liệu mới từ cơ sở dữ liệu.
        """
        data = self.fetch_attendance_logs()  # Lấy dữ liệu từ cơ sở dữ liệu
        self.update_attendance_table(data)  # Cập nhật bảng với dữ liệu mới

    def get_tab(self):
        """
        Trả về tab danh sách điểm danh.
        """
        return self.tab


# Tạo đối tượng AttendanceListApp
attendance_list_app = None

def create_attendance_list_tab(parent, width=1000, height=500):
    """
    Tạo hoặc trả về tab danh sách điểm danh. Chỉ tạo đối tượng một lần.
    """
    global attendance_list_app

    if attendance_list_app is None:
        # Nếu đối tượng chưa được tạo, tạo mới
        attendance_list_app = AttendanceListApp(parent, width, height)

    return attendance_list_app.get_tab(), attendance_list_app
