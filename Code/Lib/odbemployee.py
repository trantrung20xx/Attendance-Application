from datetime import datetime, time
import pyodbc

# Kết nối với cơ sở dữ liệu
odb = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=NITRO-5R5\SERVEROFTRUNG;'
        r'Database=Employee_Data;'
        r'UID=trantrung;'
        r'PWD=123456789')

cursor = odb.cursor()

start_time_ = [8, 0, 0]
end_time_ = [17, 0, 0]

class ODBEmployee:
    # Lấy giá trị bộ đếm hiện tại từ cơ sở dữ liệu
    @staticmethod
    def get_current_id():
        cursor.execute("SELECT ConfigValueInt FROM Configurations WHERE ConfigKey = 'Config1'")
        _id_counter = cursor.fetchone()
        if _id_counter:
            return int(_id_counter[0])
        else:
            # Thêm giá trị mặc định nếu chưa tồn tại
            cursor.execute(
                "INSERT INTO Configurations (ConfigKey, ConfigValueInt) VALUES ('Config1', 1)"
            )
            odb.commit()
            return 1

    @staticmethod
    def set_current_id(new_value):
        cursor.execute("UPDATE Configurations SET ConfigValueInt = ?, LastUpdated = GETDATE() WHERE ConfigKey = 'Config1'", (new_value,))
        odb.commit()

    # Khởi tạo bộ đếm
    # Biến _id_counter để giữ giá trị hiện tại của mã nhân viên và mã khuôn mặt
    _id_counter = get_current_id()

    @staticmethod
    def generate_id():
        # Biến _id_counter để giữ giá trị hiện tại của mã nhân viên và mã khuôn mặt
        ODBEmployee._id_counter = ODBEmployee.get_current_id()
        employee_id = f"EMP{ODBEmployee._id_counter:05d}"  # Định dạng thành EMP00001, EMP00002,...
        face_id = ODBEmployee._id_counter # face_id trùng với bộ đếm và số mã nhân viên
        ODBEmployee._id_counter += 1 # Tăng bộ đếm để thực hiện cho lần thêm nhân viên sau
        return employee_id, face_id

    def __init__(self, employee_id = None, name="unknown", face_id = None, fingerprint_data_1=None, fingerprint_data_2=None, rfid_data=None, department="unknown"):
        """
        Khởi tạo một nhân viên mới với mã tự động tăng
        """
        # Tự động gán mã nhân viên và mã khuôn mặt dựa trên bộ đếm
        self.employee_id = employee_id
        self.name = name
        self.face_id = face_id
        self.fingerprint_data_1 = fingerprint_data_1
        self.fingerprint_data_2 = fingerprint_data_2
        self.rfid_data = rfid_data
        self.department = department
        self.check_in_time = None
        self.check_out_time = None
        self.status_1 = '-' # Chưa điểm danh vào
        self.status_2 = '-' # Chưa điểm danh ra

    def save_database(self):
        """
        Cập nhật thông tin nhân viên vào cơ sở dữ liệu
        """
        cursor.execute("SELECT COUNT(*) FROM Employees WHERE EmployeeID = ?", (self.employee_id,))
        exists = cursor.fetchone()[0]
        if not exists:  # Nếu nhân viên chưa tồn tại, thêm mới
            cursor.execute(
                """
                INSERT INTO Employees (EmployeeID, Name_, FaceID, FingerprintData1, FingerprintData2, RFIDData, Department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.employee_id, self.name, self.face_id, self.fingerprint_data_1, self.fingerprint_data_2, self.rfid_data, self.department)
            )
            odb.commit()
            # Cập nhật lại bộ đếm ID trên cơ sở dữ liệu
            ODBEmployee.set_current_id(ODBEmployee._id_counter)

    def check_in(self):
        """
        Ghi nhận thời gian điểm danh vào
        """
        # Cài đặt thời gian bắt đầu/kết thúc giờ làm
        now = datetime.now() # Lấy thời gian gồm năm/tháng/ngày giờ/phút/giây
        today = now.date() # chỉ lấy năm/tháng/ngày
        start_time = datetime.combine(today, time(start_time_[0], start_time_[1], start_time_[2])) # Giờ bắt đầu ca làm
        end_time = datetime.combine(today, time(end_time_[0], end_time_[1], end_time_[2])) # Giờ kết thúc ca làm

        # Kiểm tra bản ghi thời gian điểm danh của ngày hôm nay
        cursor.execute(
            """
            SELECT LogID, CheckInTime, CheckOutTime, Status_1, Status_2
            FROM AttendanceLogs
            WHERE EmployeeID = ? AND CONVERT(DATE, CheckInTime) = ?
            """,
            (self.employee_id, today)
        )
        record_time = cursor.fetchone()
        if not record_time: # Chưa điểm danh lần nào trong ngày -> Thêm mới
            if now <= start_time: # Nếu điểm danh sớm hoặc đúng giờ
                self.status_1 = 'Đúng giờ'
            else: # Nếu muộn
                deltatime = now - start_time
                hour, remainder = divmod(deltatime.seconds, 3600) # (deltatime.seconds//3600, deltatime.seconds%3600)
                minutes = remainder // 60
                self.status_1 = f"Muộn {hour:02d} giờ {minutes:02d} phút"

            # Set giá trị cho thuộc tính check_in_time
            self.check_in_time = now.strftime("%Y-%m-%d - %H:%M:%S")

            # Cập nhật thời gian điểm danh lên cơ sở dữ liệu
            cursor.execute(
                """
                INSERT INTO AttendanceLogs (EmployeeID, CheckInTime, Status_1, Status_2)
                VALUES (?, ?, ?, ?)
                """,
                (self.employee_id, now, self.status_1, self.status_2)
            )
            odb.commit()
            return True # Cập nhật thành công
        return False # Cập nhật không thành công

    def check_out(self):
        """
        Ghi nhận thời gian điểm danh ra
        """
        # Cài đặt thời gian bắt đầu/kết thúc giờ làm
        now = datetime.now() # Lấy thời gian gồm năm/tháng/ngày giờ/phút/giây
        today = now.date() # chỉ lấy năm/tháng/ngày
        start_time = datetime.combine(today, time(start_time_[0], start_time_[1], start_time_[2])) # Giờ bắt đầu ca làm
        end_time = datetime.combine(today, time(end_time_[0], end_time_[1], end_time_[2])) # Giờ kết thúc ca làm

        # Kiểm tra bản ghi thời gian điểm danh của ngày hôm nay
        cursor.execute(
            """
            SELECT LogID, CheckInTime, CheckOutTime, Status_1, Status_2
            FROM AttendanceLogs
            WHERE EmployeeID = ? AND CONVERT(DATE, CheckInTime) = ?
            """,
            (self.employee_id, today)
        )
        record_time = cursor.fetchone()
        if record_time and record_time[3] != '-' and record_time[4] == '-': # Đã điểm danh trong ngày -> Cập nhật
            log_id, check_in_time, check_out_time, status_1, status_2 = record_time
            if now >= end_time: # Nếu điểm danh khi đã tan làm
                self.status_2 = 'Đúng giờ'
            else: # Nếu sớm hơn
                deltatime = end_time - now
                hour, remainder = divmod(deltatime.seconds, 3600) # (deltatime.seconds//3600, deltatime.seconds%3600)
                minutes = remainder // 60
                self.status_2 = f"Về trước {hour:02d} giờ {minutes:02d} phút"

            # Set giá trị cho thuộc tính check_out_time
            self.check_out_time = now.strftime("%Y-%m-%d - %H:%M:%S")

            # Cập nhật thời gian điểm danh về lên cơ sở dữ liệu
            # Cập nhật CheckOutTime và Status_2
            cursor.execute(
                """
                UPDATE AttendanceLogs
                SET CheckOutTime = ?, Status_2 = ?
                WHERE LogID = ?
                """,
                (now, self.status_2, log_id)
            )
            odb.commit()
            return True # Cập nhật thành công
        return False # Cập nhật không thành công
