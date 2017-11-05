import serial

ser = serial.Serial('/dev/ttyUSB0', timeout=2)
ser.baudrate = 9600
ser.flushInput()
ser.flushOutput()
while True:
	data_raw = ser.read(275)
	print(data_raw)