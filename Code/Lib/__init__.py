from Lib.uart_communication import UARTCommunication
from Lib import employee_management

# Khởi tạo giao tiếp UART với ESP32
uart = UARTCommunication(port="COM4", baudrate=115200, timeout=10)

# Lấy danh sách nhân viên từ cơ sở dữ liệu
employee_list = employee_management.EmployeeManagement.fetch_all_employees()
# Hàm cập nhật danh sách nhân viên từ cơ sở dữ liệu
def get_employee_list(employee_list):
    employee_list = employee_management.EmployeeManagement.fetch_all_employees()
