CREATE DATABASE Employee_Data
GO
USE Employee_Data
GO

CREATE TABLE Employees (
    EmployeeID VARCHAR(10) PRIMARY KEY,    -- Mã nhân viên
    Name_ NVARCHAR(256) NOT NULL,          -- Tên nhân viên
    FaceID INT NOT NULL UNIQUE,            -- ID khuôn mặt (duy nhất)
    FingerprintData1 VARBINARY(MAX),       -- Dữ liệu vân tay 1
    FingerprintData2 VARBINARY(MAX),       -- Dữ liệu vân tay 2
    RFIDData VARCHAR(100),                 -- Dữ liệu RFID
    Department NVARCHAR(100) DEFAULT 'unknown' -- Phòng ban
);

CREATE TABLE AttendanceLogs (
    LogID INT PRIMARY KEY IDENTITY(1,1),     -- ID tự động tăng
    EmployeeID VARCHAR(10),                  -- Mã nhân viên
    CheckInTime DATETIME,                    -- Thời gian điểm danh vào
    CheckOutTime DATETIME,                   -- Thời gian điểm danh ra
    Status_1 NVARCHAR(100),                  -- Trạng thái (Đúng giờ/Muộn)
	Status_2 NVARCHAR(100),                  -- Trạng thái (Về sớm/ Đúng giờ/ '-' chưa chấm công)
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID) -- Ràng buộc khóa ngoại
);

CREATE TABLE Configurations (
    ConfigKey VARCHAR(50) PRIMARY KEY,     -- Khóa chính định danh loại cấu hình
    ConfigValueInt INT NULL,               -- Lưu giá trị số (bộ đếm ID)
    ConfigValueBinary VARBINARY(MAX) NULL, -- Lưu nội dung file dưới dạng binary (file yml)
    LastUpdated DATETIME DEFAULT GETDATE() -- Thời gian cập nhật cuối
);

INSERT INTO Configurations (ConfigKey, ConfigValueInt) VALUES ('Config1', 1)
UPDATE Configurations SET ConfigValueInt = 7 WHERE ConfigKey = 'Config1'
DELETE FROM Employees WHERE EmployeeID = 'EMP00003'
DELETE FROM AttendanceLogs WHERE EmployeeID = 'EMP00001' AND LogID = 11

SELECT * FROM Employees
SELECT * FROM AttendanceLogs
SELECT * FROM Configurations