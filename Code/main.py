import tkinter
from tkinter.ttk import *
from Lib.attendance_live_tab import create_attendance_live_tab
from Lib.employee_management_tab import create_employee_management_tab
from Lib.addanew_employee import create_add_employee_tab
from Lib.uart_communication import UARTCommunication

# Khởi tạo giao tiếp UART với ESP32
uart = UARTCommunication(port="COM4", baudrate=115200, timeout=10)

def on_tab_change(event):
    # Kiểm tra tab hiện tại
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "Điểm danh":
        start_recognition()
    elif selected_tab == "Quản lý nhân viên":
        update_employee_list()
    else:
        stop_recognition()

window = tkinter.Tk()
window.title("Tab Interface")
window.geometry("900x500")

# Tạo một style mới để thay đổi font của tiêu đề tab
style = Style()
style.configure("TNotebook.Tab", font=("Arial", 13), padding=[5, 5])  # Đặt phông chữ và padding cho tiêu đề tab

# Tạo Notebook (thẻ tab)
notebook = Notebook(window)

# Tạo các frame cho từng tab
attendance_live_tab, start_recognition, stop_recognition = create_attendance_live_tab(notebook, width=900, height=500) # Gọi hàm từ attendance_live_tab.py
attendance_list_tab = tkinter.Frame(notebook, bg="lightgreen", width=900, height=500)
employee_management_tab, update_employee_list = create_employee_management_tab(notebook, width=500, height=500)
add_employee_tab = create_add_employee_tab(notebook, uart.send_command, uart.read_response, width=900, height=500)
# Thêm các frame vào notebook dưới dạng các tab
notebook.add(attendance_live_tab, text="Điểm danh")
notebook.add(attendance_list_tab, text="Danh sách điểm danh")
notebook.add(add_employee_tab, text="Thêm nhân viên mới")
notebook.add(employee_management_tab, text="Quản lý nhân viên")

# Đặt notebook vào cửa sổ chính
notebook.pack(expand=True, fill="both")

# Nội dung của tab Danh sách điểm danh
tkinter.Label(attendance_list_tab, text="Danh sách điểm danh", font=("Arial", 20), background="lightgreen").pack(pady=15)

# Nội dung của tab Quản lý nhân viên
tkinter.Label(employee_management_tab, text="Quản lý nhân viên", font=("Arial", 20), background="lightyellow").pack(pady=15)

# Theo dõi sự kiện chuyển đổi tab
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Chạy vòng lặp chính
window.mainloop()
