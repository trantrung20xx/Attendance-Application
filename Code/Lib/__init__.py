from Lib.uart_communication import UARTCommunication
from Lib import employee_management

# Khởi tạo giao tiếp UART với ESP32
uart = UARTCommunication(port="COM4", baudrate=115200, timeout=10)

# Lấy danh sách nhân viên từ cơ sở dữ liệu
employee_list = employee_management.EmployeeManagement.fetch_all_employees()

# Hàm cập nhật danh sách nhân viên từ cơ sở dữ liệu
def get_employee_list(employee_list):
    employee_list = employee_management.EmployeeManagement.fetch_all_employees()

# Biến bật/tắt điểm danh bằng rfid và vân tay
on_attandance = [True]
# Biến nhận thông báo gửi lên từ ESP8266 qua UART
message_uart = [None]
# Biến trạng thái cho biết có ID vân tay vừa được lưu nhưng không có nhân viên liên kết đến
unlinked_fingerprint = [False]
# Biến lưu các ID vân tay không được liên kết với nhân viên nào
unlinked_fingerprint_list = set()
