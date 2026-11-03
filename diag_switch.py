import serial
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
ser = serial.Serial('COM7', 9600, timeout=1)

def send_cmd(cmd, wait=1.0):
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    out = b""
    while ser.in_waiting:
        out += ser.read(ser.in_waiting)
        time.sleep(0.1)
    decoded = out.decode('utf-8', errors='replace')
    print(f"=== {cmd} ===")
    print(decoded)
    return decoded

send_cmd("")
send_cmd("show interfaces status | include connected")
send_cmd("show interfaces trunk")

ser.close()
