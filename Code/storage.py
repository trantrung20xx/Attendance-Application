import pyodbc
from Lib.odbemployee import ODBEmployee

# Kết nối với cơ sở dữ liệu
odb = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=NITRO-5R5\SERVEROFTRUNG;'
        r'Database=Employee_Data;'
        r'UID=trantrung;'
        r'PWD=123456789')

cursor = odb.cursor()

cursor.execute("SELECT FingerprintData1, FingerprintData2 FROM Employees")
list_pair_fingerprint_ID = cursor.fetchall()
list_fingerprint_ID = []
for pair in list_pair_fingerprint_ID:
    for ID in pair:
        if ID is not None:
            list_fingerprint_ID.append(ID)

print(list_fingerprint_ID)
list_sorted = sorted(list_fingerprint_ID)
number = [ord(i) for i in list_sorted]

print(list_sorted)
print(number)

used_fingerprint_ids = set()
for fingerprint_id in list_sorted:
    used_fingerprint_ids.add(fingerprint_id)

print(used_fingerprint_ids)

for fingerprint_id in range(1, 128):
    if bytes([fingerprint_id]) not in used_fingerprint_ids:
        print(f'Fingerprint ID {fingerprint_id} is available.')
        break

differences = [(number[i] + number[i - 1]) // 2 if (number[i] - number[i - 1]) > 1 else max(number) + 1 for i in range(1, len(list_fingerprint_ID))]
list_byte = [bytes([i]) for i in differences]
print(differences)
print(list_byte)
list_byte.append(bytes([127]))
print(max(list_byte))
print(ord(max(list_byte)))

print('-------------------------------------------------------------------------------')

print(bytes([ord(ODBEmployee.get_fingerprint_id()) + 1]))

from Lib import attendance_list_tab

print(attendance_list_tab.fetch_attendance_logs())
