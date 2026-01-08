from st3215 import ST3215

baudrate = [1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400]
baudrate_nb = 2
prev_baud_nb = 0

servo = ST3215('COM7')
print("Default baudrate:", servo.portHandler.baudrate)
print("Close port...")
servo.portHandler.closePort()
print("Reopen port with previous baudrate:", baudrate[prev_baud_nb])
servo.portHandler.baudrate = baudrate[prev_baud_nb]
servo.portHandler.openPort()
print("PingServo:", servo.PingServo(1))
status = servo.ChangeBaudrate(1, baudrate_nb)
if status != None:
    print("Baudrate change failed with status:", status)
else:
    print("Baudrate change successful")
print("Close port...")
servo.portHandler.closePort()
print("Reopen port with new baudrate:", baudrate[baudrate_nb])
servo.portHandler.baudrate = baudrate[baudrate_nb]
print("Current baudrate:", servo.portHandler.baudrate)
servo.portHandler.openPort()
print("PingServo:", servo.PingServo(1))