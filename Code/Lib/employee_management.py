from Lib.odbemployee import ODBEmployee, cursor, odb
# from odbemployee import ODBEmployee, cursor, odb

class EmployeeManagement:
    """
    Lớp quản lý các đối tượng ODBEmployee, thực hiện các chức năng liên quan đến dữ liệu nhân viên.
    """
    @staticmethod
    def fetch_all_employees():
        cursor.execute("\
            SELECT\
                EmployeeID,\
                Name_,\
                FaceID,\
                FingerprintData1,\
                FingerprintData2,\
                RFIDData,\
                Department\
            FROM Employees")
        employees = cursor.fetchall() # Lấy ra tất cả dữ liệu nhân viên từ cơ sở dữ liệu
        employee_list = [] # Danh sách nhân viên
        for emp in employees:
            employee = ODBEmployee (
                employee_id = emp[0],
                name = emp[1],
                face_id = emp[2],
                fingerprint_data_1 = emp[3],
                fingerprint_data_2 = emp[4],
                rfid_data = emp[5],
                department = emp[6]
            )
            employee_list.append(employee) # Thêm nhân viên vào danh sách
        return employee_list

    @staticmethod
    def find_employee(employee_id):
        employee_list = EmployeeManagement.fetch_all_employees()
        for employee in employee_list:
            if employee.employee_id == employee_id:
                return employee
        return None

    @staticmethod
    def create_employee(name, fingerprint_data_1=None, fingerprint_data_2=None, rfid_data=None, department="unknown"):
        """
        Tạo mới một nhân viên và lưu vào cơ sở dữ liệu.
        """
         # Sử dụng phương thức generate_id để tạo ID mới
        employee_id, face_id = ODBEmployee.generate_id()
        new_employee = ODBEmployee(
            employee_id = employee_id,
            name = name,
            face_id = face_id,
            fingerprint_data_1 = fingerprint_data_1,
            fingerprint_data_2 = fingerprint_data_2,
            rfid_data = rfid_data,
            department = department
        )
        # Thêm nhân viên mới vòa cơ sở dữ liệu
        new_employee.save_database()
        return new_employee

    @staticmethod
    def update_employee(employee_id, name=None, fingerprint_data_1 = None, fingerprint_data_2=None, rfid_data=None, department=None):
        """
        Cập nhật thông tin nhân viên trong cơ sở dữ liệu.
        """
        # Kiểm tra xem nhân viên có tồn tại không
        cursor.execute("SELECT * FROM Employees WHERE EmployeeID = ?", (employee_id,))
        employee = cursor.fetchone()
        if not employee: # Nếu không tồn tại
            return False
        # Cập nhật thông tin nếu có thay đổi
        if name:
            cursor.execute("UPDATE Employees SET Name_ = ? WHERE EmployeeID = ?", (name, employee_id))
        if fingerprint_data_1:
            cursor.execute("UPDATE Employees SET FingerprintData1 = ? WHERE EmployeeID = ?", (fingerprint_data_1, employee_id))
        if fingerprint_data_2:
            cursor.execute("UPDATE Employees SET FingerprintData2 = ? WHERE EmployeeID = ?", (fingerprint_data_2, employee_id))
        if rfid_data:
            cursor.execute("UPDATE Employees SET RFIDData = ? WHERE EmployeeID = ?", (rfid_data, employee_id))
        if department:
            cursor.execute("UPDATE Employees SET Department =? WHERE EmployeeID =?", (department, employee_id))
        odb.commit() # Lưu thay đổi
        return True

    @staticmethod
    def delete_employee(employee_id):
        """
        Xóa nhân viên khỏi cơ sở dữ liệu.
        """
        # Kiểm tra xem nhân viên có tồn tại không
        cursor.execute("SELECT * FROM Employees WHERE EmployeeID = ?", (employee_id,))
        employee = cursor.fetchone()
        if not employee: # Nếu không tồn tại
            return False
        # Xóa nhân viên
        cursor.execute("DELETE FROM Employees WHERE EmployeeID = ?", (employee_id,))
        odb.commit() # Lưu thay đổi
        return True



