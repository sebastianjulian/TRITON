import serial
print("BEFORE INIT")
LORA_SERIAL_DEVICE = '/dev/serial0'
LORA_SERIAL_BAUD_RATE = 9600
lora = serial.Serial(LORA_SERIAL_DEVICE, baudrate=LORA_SERIAL_BAUD_RATE, timeout=3.0)
print("AFTER INIT")
print("BEFORE SEND")
lora.write('test'.encode('utf-8'))
print("AFTER SEND")