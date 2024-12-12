import tkinter
from tkinter.ttk import *
import threading
from Lib.attendance_live_tab import create_attendance_live_tab, attandance_with_uart_data
from Lib.employee_management_tab import create_employee_management_tab
from Lib.addanew_employee import create_add_employee_tab
from Lib import uart, employee_list, get_employee_list, on_attandance

uart_thread = [None]  # Quản lý luồng UART

def on_tab_change(event):
    # Kiểm tra tab hiện tại
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "Điểm danh":
        get_employee_list(employee_list) # Cập nhật lại danh sách nhân viên
        stop_recognition() # Tắt điểm danh khuôn mặt
        on_attandance[0] = True # Bật lại chức năng điểm danh với vân tay và rfid
        if not uart_thread[0] or not uart_thread[0].is_alive():
            uart_thread[0] = threading.Thread(target=attandance_with_uart_data, args=(info_labels,))
            uart_thread[0].daemon = True
            uart_thread[0].start()
    elif selected_tab == "Quản lý nhân viên":
        update_employee_list()
        on_attandance[0] = False # Tắt chức năng điểm danh với rfid và vân tay
        stop_recognition() # Tắt điểm danh khuôn mặt
    elif selected_tab == "Danh sách điểm danh":
        stop_recognition() # Tắt điểm danh khuôn mặt
        on_attandance[0] = True # Bật lại chức năng điểm danh với vân tay và rfid
        if not uart_thread[0] or not uart_thread[0].is_alive():
            uart_thread[0] = threading.Thread(target=attandance_with_uart_data, args=(info_labels,))
            uart_thread[0].daemon = True
            uart_thread[0].start()
    elif selected_tab == "Thêm nhân viên mới":
        on_attandance[0] = False # Tắt chức năng điểm danh với rfid và vân tay
        stop_recognition() # Tắt điểm danh khuôn mặt

window = tkinter.Tk()
window.title("Tab Interface")
window.geometry("1000x500")

# Tạo một style mới để thay đổi font của tiêu đề tab
style = Style()
style.configure("TNotebook.Tab", font=("Arial", 13), padding=[5, 5])  # Đặt phông chữ và padding cho tiêu đề tab

# Tạo Notebook (thẻ tab)
notebook = Notebook(window)

# Tạo các frame cho từng tab
attendance_live_tab, start_recognition, stop_recognition, info_labels = create_attendance_live_tab(notebook, width=1000, height=500) # Gọi hàm từ attendance_live_tab.py
attendance_list_tab = tkinter.Frame(notebook, bg="lightgreen", width=1000, height=500)
employee_management_tab, update_employee_list = create_employee_management_tab(notebook, width=1000, height=500)
add_employee_tab = create_add_employee_tab(notebook, uart.send_command, uart.read_response, width=1000, height=500)
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

# Bắt đầu đọc dữ liệu vân tay và rfid từ ESP8266 để điểm danh
if not uart_thread[0] or not uart_thread[0].is_alive():
    uart_thread[0] = threading.Thread(target=attandance_with_uart_data, args=(info_labels,))
    uart_thread[0].daemon = True
    uart_thread[0].start()
stop_recognition()

# Chạy vòng lặp chính
window.mainloop()
