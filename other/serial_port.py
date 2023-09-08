# sudo dmesg | tail
# sudo usermod -a -G tty [username]
# sudo usermod -a -G dialout [username]
# ls -l /dev/tty
# 
import time
import serial

def open_serial_port():
	serial_port = serial.Serial(
	port='/dev/ttyUSB0', 
	baudrate = 9600,
	timeout = 0.1) # float seconds
	return serial_port
	
	
def send_mess_to_serial_port(Yaw_angle, Pith_angle, Cam_mode):
	mess = ('$'+str(Yaw_angle)+','+str(Pith_angle)+','+str(Cam_mode)+';')
	print('mess', mess)
	serial_port.write(mess.encode())
	print('mess.encode()', mess.encode('UTF-8'))	

try:
	serial_port = 	open_serial_port()
	serial_port.isOpen()
except:
	print('Serial not open')
	exit(0)

for i in range(90):
	send_mess_to_serial_port(90, -i, 1)
	time.sleep(0.1)

	
