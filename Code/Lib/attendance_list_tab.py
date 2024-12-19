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

        self.tab = tkinter.Frame(self.parent, bg="#e6f2ff", width=self.width, height=self.height)
        self.tree = None
        self.scrollbar = None
        self.create_widgets()

    def create_widgets(self):
        """
        Tạo các widget (như Label, Treeview) cho tab danh sách điểm danh.
        """
        # Tiêu đề
        tkinter.Label(
            self.tab,
            text="📋 Danh sách điểm danh",
            font=("Arial", 28, "bold"),
            bg="#e6f2ff",
            fg="#1f4e79"  # Màu xanh đậm
        ).pack(pady=15)

        # Tạo khung chứa bảng và thanh cuộn
        frame = tkinter.Frame(self.tab, bg="#e6f2ff")
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Cấu hình bảng Treeview
        columns = ("EmployeeID", "Name", "Department", "CheckInTime", "Status1", "CheckOutTime", "Status2")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", style="Custom.Treeview")

        # Đặt tiêu đề và định dạng các cột
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=140)

        # Thêm thanh cuộn dọc
        self.scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Đặt vị trí thanh cuộn và bảng Treeview
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Cấu hình khung chứa
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Thêm style cho Treeview
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            font=("Arial", 12),  # Font chữ
            rowheight=30,  # Chiều cao mỗi dòng
            background="#f9f9f9",  # Màu nền
            foreground="#333",  # Màu chữ
            fieldbackground="#f9f9f9",  # Màu nền cho ô nhập
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=("Arial", 14, "bold"),  # Font chữ lớn hơn cho tiêu đề
            background="#1f4e79",  # Màu xanh đậm
            foreground="white",  # Màu chữ trắng
            relief="raised",  # Tạo hiệu ứng nổi cho heading
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#87cefa")],  # Màu nền khi chọn dòng
            foreground=[("selected", "#000000")],  # Màu chữ khi chọn dòng
        )

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
            print(f"Lỗi khi lấy dữ liệu điểm danh: {e}")
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
        Cập nhật dữ liệu mới vào Treeview với màu sắc xen kẽ giữa các dòng.
        """
        # Xóa dữ liệu cũ
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Thêm dữ liệu mới với màu sắc xen kẽ
        for index, record in enumerate(data):
            formatted_record = self.format_row(record)
            # Xác định tag cho màu dòng
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=formatted_record, tags=(tag,))

        # Đặt màu sắc cho các tag
        self.tree.tag_configure('evenrow', background='#ffffff')  # Màu sáng hơn
        self.tree.tag_configure('oddrow', background='#f0f8ff')   # Màu đậm hơn

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
