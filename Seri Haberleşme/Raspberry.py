import serial
import json
import time
import threading

# UART ayarları
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)  # Raspberry Pi'deki UART portu

received_data = ""
start_char = '<'
end_char = '>'

# Mesaj alma fonksiyonu
def receive_data():
    global received_data
    while True:
        if ser.in_waiting > 0:
            char = ser.read().decode()
            if char == start_char:
                received_data = ""
            elif char == end_char:
                print(f"Received JSON: {received_data}")
                try:
                    data = json.loads(received_data)
                    print(data)
                except json.JSONDecodeError:
                    print("Invalid JSON data received")
            else:
                received_data += char

# Mesaj gönderme fonksiyonu
def send_data():
    while True:
        data = {
            "name": "raspberry",
            "x": 150,
            "y": 200
        }
        json_data = json.dumps(data)
        send_data = f'<{json_data}>'
        ser.write(send_data.encode())
        print(f"Sent: {send_data}")
        time.sleep(1)  # 1 saniye bekle

# Alıcı ve gönderici fonksiyonlarını ayrı threadlerde çalıştır
receive_thread = threading.Thread(target=receive_data)
send_thread = threading.Thread(target=send_data)

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()
