from Lib.uart_communication import UARTCommunication

# Khởi tạo giao tiếp UART với ESP32
uart = UARTCommunication(port="COM4", baudrate=115200, timeout=10)
