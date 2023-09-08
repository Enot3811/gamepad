import sys
import inputs
import serial
# Подключаем джойстик
#print(inputs.devices.all_devices)
pads = inputs.devices.gamepads
if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")


# Открываем серийный порт
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


Yaw_angle = 0
Pith_angle = 0
Cam_mode = 1


while True:

	events = inputs.get_gamepad()

	for event in events:

		#print('event.ev_type', event.ev_type)
		#print('event.code', event.code)
		#print('event.state', event.state)
		
		if event.code == 'ABS_X':
			Yaw_angle = int(event.state)
			Yaw_angle = Yaw_angle - 128
			print('Yaw_angle', Yaw_angle)
			
		if event.code == 'ABS_Y':
			Pith_angle = int(event.state)
			Pith_angle = Pith_angle - 127
			if Pith_angle > 0:
				Pith_angle = int(Pith_angle*(45/128))
			print('Pith_angle', Pith_angle)
			
		if event.code == 'BTN_TOP':
			if int(event.state) == 1:
				if Cam_mode == 0:
					Cam_mode = 1
				else:
					Cam_mode = 0
			print('Cam_mode', Cam_mode)
			

		if event.code == 'BTN_SOUTH' and event.state == 1:
			print('Celebrate!')
			
		send_mess_to_serial_port(Yaw_angle, Pith_angle, Cam_mode)


