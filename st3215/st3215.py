import threading
import time
import math

from .port_handler import *
from .protocol_packet_handler import *
from .group_sync_write import *
from .group_sync_read import *
from .values import *


__all__ = ['ST3215']


class ST3215(protocol_packet_handler):

    def __init__(self, device):

        self.portHandler = PortHandler(device)
        
        if not self.portHandler.openPort():
            raise ValueError(f"Could not open port: {device}")

        protocol_packet_handler.__init__(self, self.portHandler)

        self.groupSyncWrite = GroupSyncWrite(self, STS_ACC, 7)
        self.lock = threading.Lock()


    def PingServo(self, sts_id):
        """
        Check the presence of a servo.

        :param sts_id: Servo ID

        :return: True in case of success otherwise False
        """
        model, comm, error = self.ping(sts_id)
        if comm != COMM_SUCCESS or model == 0 or error != 0:
            return False
        return True


    def ListServos(self):
        """
        Scan the bus to determine all servo present

        :return: A list of servo ID
        """
        servos=[]
        for id in range(0, 254):
            if self.PingServo(id):
                servos.append(id)

        return servos


    def ReadLoad(self, sts_id):
        """
        Load of the servo. 
        Load value is determined by: The voltage duty cycle of the current control output driving motor

        :param sts_id: Servo ID

        :return: Load value in percentage. None in case of error.
        """
        load, comm, error = self.read1ByteTxRx(sts_id, STS_PRESENT_LOAD_L)
        if comm == 0 and error == 0:
            return load * 0.1
        else:
            return None

    def ReadVoltage(self, sts_id):
        """
        Current Voltage of the servo. 

        :param sts_id: Servo ID

        :return: Current Voltage in V. None in case of error.
        """
        voltage, comm, error = self.read1ByteTxRx(sts_id, STS_PRESENT_VOLTAGE)
        if comm == 0 and error == 0:
            return voltage * 0.1
        else:
            return None

    def ReadCurrent(self, sts_id):
        """
        Current current of the servo. 

        :param sts_id: Servo ID

        :return: Current current in mA. None in case of error.
        """
        current, comm, error = self.read1ByteTxRx(sts_id, STS_PRESENT_CURRENT_L)
        if comm == 0 and error == 0:
            return current * 6.5
        else:
            return None

    def ReadTemperature(self, sts_id):
        """
        Current temperature of the servo. 

        :param sts_id: Servo ID

        :return: Current temperature in °C. None in case of error.
        """
        temperature, comm, error =  self.read1ByteTxRx(sts_id, STS_PRESENT_TEMPERATURE)
        if comm == 0 and error == 0:
            return temperature
        else:
            return None


    def ReadAccelaration(self, sts_id):
        """
        Current value of the acceleration of the servo. 

        :param sts_id: Servo ID

        :return: Current acceleration value. None in case of error.
        """
        acc, comm, error =  self.read1ByteTxRx(sts_id, STS_ACC)
        if comm == 0 and error == 0:
            return acc
        else:
            return None


    def ReadMode(self, sts_id):
        """
        Current mode of the servo. 
          - 0: Position Mode
          - 1: Constant speed mode
          - 2: PWM Mode
          - 3: Step servo mode

        :param sts_id: Servo ID

        :return: Current mode. None in case of error.
        """
        mode, comm, error =  self.read1ByteTxRx(sts_id, STS_MODE)
        if comm == 0 and error == 0:
            return mode
        else:
            return None


    def ReadCorrection(self, sts_id):
        """
        Current value of position correction for the servo. 

        :param sts_id: Servo ID

        :return: Current correction value. None in case of error.
        """
        correction, comm, error =  self.read2ByteTxRx(sts_id, STS_OFS_L)
        if comm == 0 and error == 0:
            mask = 0x07FFF
            bits = correction & mask
            if (correction & 0x0800) != 0:
                bits = -1 * (bits & 0x7FF)
            return bits
        else:
            return None


    def IsMoving(self, sts_id):
        """
        Is the servo moving

        :param sts_id: Servo ID

        :return: True is the servo is moving otherwise False. None in case of error.
        """
        moving, comm, error =  self.read1ByteTxRx(sts_id, STS_MOVING)
        if comm == 0 and error == 0:
            return bool(moving)
        else:
            return None


    def SetAcceleration(self, sts_id, acc):
        """
        Configure the Acceleration value for the servo

        :param sts_id: Servo ID
        :param acc: Acceleration value (0-254). Unit: 100 step/s^2)

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [acc]
        comm, error = self.writeTxRx(sts_id, STS_ACC, len(txpacket), txpacket)
        if comm == 0 and error == 0:
            return True
        else:
            return None


    def SetSpeed(self, sts_id, speed):
        """
        Configure the Speed value for the servo

        :param sts_id: Servo ID
        :param acc: Speed value (0-3400). Unit: Step/s

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [self.sts_lobyte(speed), self.sts_hibyte(speed)]
        comm, error = self.writeTxRx(sts_id, STS_GOAL_SPEED_L, len(txpacket), txpacket)
        if comm == 0 and error == 0:
            return True
        else:
            return None


    def StopServo(self, sts_id):
        """
        Stop the servo (Set torque to 0)

        :param sts_id: Servo ID

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [0]
        comm, error = self.writeTxRx(sts_id, STS_TORQUE_ENABLE, len(txpacket), txpacket)
        if comm == 0 and error == 0:
            return True
        else:
            return None


    def StartServo(self, sts_id):
        """
        Start the servo (Set torque to 1)

        :param sts_id: Servo ID

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [1]
        return self.writeTxRx(sts_id, STS_TORQUE_ENABLE, len(txpacket), txpacket)



    def SetMode(self, sts_id, mode):
        """
        Configure the operational mode for the servo (Position, rotating, PWM, step)

        :param sts_id: Servo ID
        :param mode: Mode ID (0, 1, 2 or 3 - Cf register values)

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [mode]
        return self.writeTxRx(sts_id, STS_MODE, len(txpacket), txpacket)



    def CorrectPosition(self, sts_id, correction):
        """
        Add a position correction

        :param sts_id: Servo ID
        :param correction: correction (in steps, could be negative)

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        corr = abs(correction)
        if corr > MAX_CORRECTION:
            corr = MAX_CORRECTION

        txpacket = [self.sts_lobyte(corr), self.sts_hibyte(corr)]

        if correction < 0:
            txpacket[1] |= (1 << 3)

        return self.writeTxRx(sts_id, STS_OFS_L, len(txpacket), txpacket)


    def Rotate(self, sts_id, speed):
        """
        Start rotating

        :param sts_id: Servo ID
        :param speed: servo speed (could be negative, if so rotate counterwise)

        :return: True if the configuration a been succesfully set. None in case of error.
        """

        self.SetMode(sts_id, 1)

        abs_speed = abs(speed)
        if abs_speed > MAX_SPEED:
            abs_speed = MAX_SPEED

        txpacket = [self.sts_lobyte(abs_speed), self.sts_hibyte(abs_speed)]

        if speed < 0:
            txpacket[1] |= (1 << 7)

        return self.writeTxRx(sts_id, STS_GOAL_SPEED_L, len(txpacket), txpacket)



    def getBlockPosition(self, sts_id):
        """
        Get the next blocking position

        :param sts_id: Servo ID

        :return: blocking position. None in case of error.
        """

        stop_matches = 0
        while True:
            moving = self.IsMoving(sts_id)
            if moving == None:
                self.SetMode(sts_id, 0)
                self.StopServo(sts_id)
                return None

            if moving == False:
                position = self.ReadPosition(sts_id)
                self.SetMode(sts_id, 0)
                self.StopServo(sts_id)

                if position == None:
                    return None
                else:
                    stop_matches += 1
                    if stop_matches > 4:
                        return position
            else:
                stop_matches = 0

            time.sleep(0.02)



    def DefineMiddle(self, sts_id):
        """
        Define the 2048 position (Set torque to 128)

        :param sts_id: Servo ID

        :return: True if the configuration a been succesfully set. None in case of error.
        """
        txpacket = [128]
        comm, error = self.writeTxRx(sts_id, STS_TORQUE_ENABLE, len(txpacket), txpacket)
        if comm == 0 and error == 0:
            return True
        else:
            return None



    def TareServo(self, sts_id):
        """
        Tare a Servo: Find its min and max position, then configure the new 0 position of the servo course

        WARNING: Must only be use for a servo that has at least one blocking position. Never use this function for a free rotation servo.

        :param sts_id: Servo ID

        :return: min and max position in the servo course. None in case of error.
        """

        if self.CorrectPosition(sts_id, 0) is None:
            return None, None

        time.sleep(0.5)

        self.SetAcceleration(sts_id, 100)
        self.Rotate(sts_id, -250)
        time.sleep(0.5)

        min_position = self.getBlockPosition(sts_id)


        self.Rotate(sts_id, 250)
        time.sleep(0.5)

        max_position = self.getBlockPosition(sts_id)

        if min_position is not None and max_position is not None:

            # Now, set the middle of the path to 2048
            if min_position >= max_position:
                distance = int(((MAX_POSITION - min_position + max_position) / 2))
            else:
                distance = int(((max_position - min_position) / 2))


            if min_position > int(MAX_POSITION/2):
                corr = min_position - MAX_POSITION - 1
            else:
                corr = min_position


            if self.CorrectPosition(sts_id, corr) is not None:
                min_position = 0
                max_position = distance * 2
                time.sleep(0.5)

                self.MoveTo(sts_id, distance)

        return min_position, max_position



    def MoveTo(self, sts_id, position, speed = 2400, acc = 50, wait = False):
        """
        Move the servo to a pre defined position

        :param sts_id: Servo ID
        :param position: New position of the Servo
        :param speed: Move speed in step/s (facultative, 2400 by default)
        :param acc: Accelaration speed in step/s² (facultative, 50 by default)
        :param wait: Wait the position to be reached before the function return (facultative, False by default)

        :return: True. None in case of error.
        """

        res_mode = self.SetMode(sts_id, 0)
        res_acc = self.SetAcceleration(sts_id, acc)
        res_speed = self.SetSpeed(sts_id, speed)

        if res_acc == None or res_speed == None or res_mode == None:
            return None

        curr_pos = self.ReadPosition(sts_id) 

        res_pos = self.WritePosition(sts_id, position)
        if res_pos == None:
            return None

        if wait == True:
            if position == None:
                return None
            else:
                distance = abs(position - curr_pos)

            time_to_speed = speed / (acc * 100)

            distance_acc = 0.5 * (acc * 100) * time_to_speed ** 2

            if distance_acc >= distance:
                time_wait = math.sqrt(2 * distance / acc)
            else:
                remain_distance = distance - distance_acc
                time_wait = time_to_speed + (remain_distance / speed)

            time.sleep(time_wait)

        return True



    def WritePosition(self, sts_id, position):
        txpacket = [self.sts_lobyte(position), self.sts_hibyte(position)]
        comm, error = self.writeTxRx(sts_id, STS_GOAL_POSITION_L, len(txpacket), txpacket)
        if comm == 0 and error == 0:
            return True
        else:
            return None


    def ReadStatus(self, sts_id):
        """
        Get the sensors status

        :param sts_id: Servo ID

        :return: dict of sensor status in case of success, otherwise None
        """
        status_bits = ["Voltage", "Sensor", "Temperature", "Current", "Angle", "Overload"]

        status = {}

        status_byte, comm, error =  self.read1ByteTxRx(sts_id, STS_STATUS)
        if comm != 0 or error != 0:
            return None


        for i in range(6):
            if status_byte & (1 << i):
                status[status_bits[i]] = False
            else:
                status[status_bits[i]] = True

        return status


    def ReadPosition(self, sts_id):
        """
        Get the current position

        :param sts_id: Servo ID

        :return: position in case of success, otherwise None
        """
        position, comm, error = self.read2ByteTxRx(sts_id, STS_PRESENT_POSITION_L)
        if comm == 0 and error == 0:
            return position
        else:
            return None

    def ReadSpeed(self, sts_id):
        """
        Get the current speed

        :param sts_id: Servo ID

        :return: speed in case of success, otherwise None
        """
        sts_present_speed, sts_comm_result, sts_error = self.read2ByteTxRx(sts_id, STS_PRESENT_SPEED_L)
        return self.sts_tohost(sts_present_speed, 15), sts_comm_result, sts_error



    def LockEprom(self, sts_id):
        """
        Lock the servo Eeprom.

        :param sts_id: Servo ID

        :return: 0 in case of success
        """
        return self.write1ByteTxOnly(sts_id, STS_LOCK, 1)

    def UnLockEprom(self, sts_id):
        """
        Unlock the servo Eeprom.

        :param sts_id: Servo ID

        :return: 0 in case of success
        """
        return self.write1ByteTxOnly(sts_id, STS_LOCK, 0)

    def ChangeId(self, sts_id, new_id):
        """
        Change ID of a Servo.

        :param sts_id: Actual ID for the servo (1 for a brand new servo)
        :param new_id: New ID for the servo

        :return: None when sucedeed otherwise the error message 
        """
        if isinstance(new_id, int) and 0 <= new_id <= 253:
            if not self.PingServo(sts_id):
                return f"Could not find servo: {sts_id}" 

            if self.UnLockEprom(sts_id) != COMM_SUCCESS:
                return "Could not unlock Eprom" 

            if self.write1ByteTxOnly(sts_id, STS_ID, new_id) != COMM_SUCCESS:
                return "Could not change Servo ID" 

            self.LockEprom(sts_id)
            return None
        else:
            return "new_id is not between 0 and 253" 

    def ChangeBaudrate(self, sts_id, new_baudrate):
        """
        Change Baudrate of a Servo.

        :param sts_id: Actual ID for the servo
        :param new_baudrate: New baudrate for the servo (in bps)

        :return: None when sucedeed otherwise the error message 
        """
        if isinstance(new_baudrate, int) and 0 <= new_baudrate <= 7:
            
            if not self.PingServo(sts_id):
                return f"Could not find servo: {sts_id}" 

            if self.UnLockEprom(sts_id) != COMM_SUCCESS:
                return "Could not unlock Eprom" 

            if self.write1ByteTxOnly(sts_id, STS_BAUD_RATE, new_baudrate) != COMM_SUCCESS:
                return "Could not change Servo Baudrate" 

            self.LockEprom(sts_id)
            return None
        else:
            return "baudrate is not valid"
    

