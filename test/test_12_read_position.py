from st3215 import ST3215

baudrate = [1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400]
baudrate_nb = 0
prev_baud_nb = 0

servo = ST3215('COM7')
print("Default baudrate:", servo.portHandler.baudrate)
print("Close port...")
servo.portHandler.closePort()
print("Reopen port with the right baudrate:", baudrate[baudrate_nb])
servo.portHandler.baudrate = baudrate[baudrate_nb]
servo.portHandler.openPort()
print("Position:", servo.ReadPosition(1))