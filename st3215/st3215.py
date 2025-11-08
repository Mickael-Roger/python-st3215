import threading
import math
import warnings

from .port_handler import *
from .protocol_packet_handler import *
from .group_sync_write import *
from .group_sync_read import *
from .values import *
from .errors import PortError

logger = logging.getLogger(__name__)


__all__ = ["ST3215"]


class ST3215(ProtocolPacketHandler):
    def __init__(self, device: str):
        logger.info(f"Initializing ST3215 controller on device: {device}")
        self.portHandler = PortHandler(device)

        if not self.portHandler.port_open():
            logger.error(f"Failed to open port: {device}")
            raise PortError(f"Could not open port: {device}")

        ProtocolPacketHandler.__init__(self, self.portHandler)

        self.groupSyncWrite = GroupSyncWrite(self, STS_ACC, 7)
        self.lock = threading.Lock()
        logger.info(f"ST3215 controller initialized successfully")

    # ============================================================================
    # DISCOVERY & COMMUNICATION METHODS
    # ============================================================================

    def ping_servo(self, servo_id: int) -> bool:
        """
        Check the presence of a servo.

        :param servo_id: Servo ID

        :return: True in case of success otherwise False
        """
        logger.debug(f"Pinging servo {servo_id}")
        model, comm, error = self.ping(servo_id)
        if comm != COMM_SUCCESS or model == 0 or error != 0:
            logger.debug(f"Servo {servo_id} not responding")
            return False
        logger.debug(f"Servo {servo_id} is online")
        return True

    def scan_servos(self) -> List[int]:
        """
        Scan the bus to determine all servos present.

        :return: A list of servo IDs
        """
        logger.info("Scanning for servos on the bus...")
        servos: List[int] = []
        for servo_id in range(0, 254):
            if self.ping_servo(servo_id):
                servos.append(servo_id)

        logger.info(f"Found {len(servos)} servo(s): {servos}")
        return servos

    # ============================================================================
    # READ SENSOR METHODS - Telemetry
    # ============================================================================

    def read_load(self, servo_id: int) -> Optional[float]:
        """
        Read the load of the servo.
        Load value is determined by: The voltage duty cycle of the current control output driving motor.

        :param servo_id: Servo ID

        :return: Load value in percentage. None in case of error.
        """
        logger.debug(f"Reading load from servo {servo_id}")
        load, comm, error = self.read_tx_rx_1byte(servo_id, STS_PRESENT_LOAD_L)
        if comm == COMM_SUCCESS and error == 0:
            load_percent = load * 0.1
            logger.debug(f"Servo {servo_id} load: {load_percent}%")
            return load_percent
        else:
            logger.warning(
                f"Failed to read load from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_voltage(self, servo_id: int) -> Optional[float]:
        """
        Read the current voltage of the servo.

        :param servo_id: Servo ID

        :return: Current voltage in V. None in case of error.
        """
        logger.debug(f"Reading voltage from servo {servo_id}")
        voltage, comm, error = self.read_tx_rx_1byte(servo_id, STS_PRESENT_VOLTAGE)
        if comm == COMM_SUCCESS and error == 0:
            voltage_v = voltage * 0.1
            logger.debug(f"Servo {servo_id} voltage: {voltage_v}V")
            return voltage_v
        else:
            logger.warning(
                f"Failed to read voltage from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_current(self, servo_id: int) -> Optional[float]:
        """
        Read the current current (amperage) of the servo.

        :param servo_id: Servo ID

        :return: Current current in mA. None in case of error.
        """
        logger.debug(f"Reading current from servo {servo_id}")
        current, comm, error = self.read_tx_rx_1byte(servo_id, STS_PRESENT_CURRENT_L)
        if comm == COMM_SUCCESS and error == 0:
            current_ma = current * 6.5
            logger.debug(f"Servo {servo_id} current: {current_ma}mA")
            return current_ma
        else:
            logger.warning(
                f"Failed to read current from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_temperature(self, servo_id: int) -> Optional[int]:
        """
        Read the current temperature of the servo.

        :param servo_id: Servo ID

        :return: Current temperature in °C. None in case of error.
        """
        logger.debug(f"Reading temperature from servo {servo_id}")
        temperature, comm, error = self.read_tx_rx_1byte(
            servo_id, STS_PRESENT_TEMPERATURE
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} temperature: {temperature}°C")
            return temperature
        else:
            logger.warning(
                f"Failed to read temperature from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_position(self, servo_id: int) -> Optional[int]:
        """
        Read the current position of the servo.

        :param servo_id: Servo ID

        :return: Position in case of success, otherwise None
        """
        logger.debug(f"Reading position from servo {servo_id}")
        position, comm, error = self.read_tx_rx_2bytes(servo_id, STS_PRESENT_POSITION_L)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} position: {position}")
            return position
        else:
            logger.warning(
                f"Failed to read position from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_speed(self, servo_id: int) -> Tuple[int, int, int]:
        """
        Read the current speed of the servo.

        :param servo_id: Servo ID

        :return: Tuple of (speed, comm_result, error)
        """
        logger.debug(f"Reading speed from servo {servo_id}")
        sts_present_speed, sts_comm_result, sts_error = self.read_tx_rx_2bytes(
            servo_id, STS_PRESENT_SPEED_L
        )
        speed = sts_tohost(sts_present_speed, 15)
        if sts_comm_result == COMM_SUCCESS and sts_error == 0:
            logger.debug(f"Servo {servo_id} speed: {speed}")
        else:
            logger.warning(
                f"Failed to read speed from servo {servo_id}: comm={sts_comm_result}, error={sts_error}"
            )
        return speed, sts_comm_result, sts_error

    def read_status(self, servo_id: int) -> Optional[dict]:
        """
        Read the sensor status of the servo.

        :param servo_id: Servo ID

        :return: Dict of sensor status in case of success, otherwise None
        """
        logger.debug(f"Reading status from servo {servo_id}")
        status_bits = [
            "Voltage",
            "Sensor",
            "Temperature",
            "Current",
            "Angle",
            "Overload",
        ]

        status = {}

        status_byte, comm, error = self.read_tx_rx_1byte(servo_id, STS_STATUS)
        if comm != 0 or error != 0:
            logger.warning(
                f"Failed to read status from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

        for i in range(6):
            if status_byte & (1 << i):
                status[status_bits[i]] = False
            else:
                status[status_bits[i]] = True

        logger.debug(f"Servo {servo_id} status: {status}")
        return status

    def is_moving(self, servo_id: int) -> Optional[bool]:
        """
        Check if the servo is currently moving.

        :param servo_id: Servo ID

        :return: True if the servo is moving, False otherwise. None in case of error.
        """
        logger.debug(f"Checking if servo {servo_id} is moving")
        moving, comm, error = self.read_tx_rx_1byte(servo_id, STS_MOVING)
        if comm == COMM_SUCCESS and error == 0:
            is_moving = bool(moving)
            logger.debug(f"Servo {servo_id} moving: {is_moving}")
            return is_moving
        else:
            logger.warning(
                f"Failed to check if servo {servo_id} is moving: comm={comm}, error={error}"
            )
            return None

    # ============================================================================
    # READ CONFIGURATION METHODS
    # ============================================================================

    def read_acceleration(self, servo_id: int) -> Optional[int]:
        """
        Read the current acceleration value of the servo.

        :param servo_id: Servo ID

        :return: Current acceleration value. None in case of error.
        """
        logger.debug(f"Reading acceleration from servo {servo_id}")
        acc, comm, error = self.read_tx_rx_1byte(servo_id, STS_ACC)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} acceleration: {acc}")
            return acc
        else:
            logger.warning(
                f"Failed to read acceleration from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_mode(self, servo_id: int) -> Optional[int]:
        """
        Read the current operational mode of the servo.
          - 0: Position Mode
          - 1: Constant speed mode
          - 2: PWM Mode
          - 3: Step servo mode

        :param servo_id: Servo ID

        :return: Current mode. None in case of error.
        """
        logger.debug(f"Reading mode from servo {servo_id}")
        mode, comm, error = self.read_tx_rx_1byte(servo_id, STS_MODE)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} mode: {mode}")
            return mode
        else:
            logger.warning(
                f"Failed to read mode from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def read_position_correction(self, servo_id: int) -> Optional[int]:
        """
        Read the current value of position correction for the servo.

        :param servo_id: Servo ID

        :return: Current correction value. None in case of error.
        """
        logger.debug(f"Reading position correction from servo {servo_id}")
        correction, comm, error = self.read_tx_rx_2bytes(servo_id, STS_OFS_L)
        if comm == COMM_SUCCESS and error == 0:
            mask = 0x07FFF
            bits = correction & mask
            if (correction & 0x0800) != 0:
                bits = -1 * (bits & 0x7FF)
            logger.debug(f"Servo {servo_id} position correction: {bits}")
            return bits
        else:
            logger.warning(
                f"Failed to read position correction from servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    # ============================================================================
    # WRITE CONFIGURATION METHODS
    # ============================================================================

    def set_acceleration(self, servo_id: int, acceleration: int) -> Optional[bool]:
        """
        Configure the acceleration value for the servo.

        :param servo_id: Servo ID
        :param acceleration: Acceleration value (0-254). Unit: 100 step/s²

        :return: True if successfully set, None in case of error.
        """
        logger.debug(f"Setting acceleration for servo {servo_id} to {acceleration}")
        txpacket = [acceleration]
        comm, error = self.write_tx_rx(servo_id, STS_ACC, len(txpacket), txpacket)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} acceleration set successfully")
            return True
        else:
            logger.warning(
                f"Failed to set acceleration for servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def set_speed(self, servo_id: int, speed: int) -> Optional[bool]:
        """
        Configure the speed value for the servo.

        :param servo_id: Servo ID
        :param speed: Speed value (0-3400). Unit: Step/s

        :return: True if successfully set, None in case of error.
        """
        logger.debug(f"Setting speed for servo {servo_id} to {speed}")
        txpacket = [self.sts_lobyte(speed), self.sts_hibyte(speed)]
        comm, error = self.write_tx_rx(
            servo_id, STS_GOAL_SPEED_L, len(txpacket), txpacket
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} speed set successfully")
            return True
        else:
            logger.warning(
                f"Failed to set speed for servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def set_mode(self, servo_id: int, mode: int) -> Tuple[Optional[bool], int]:
        """
        Configure the operational mode for the servo.

        :param servo_id: Servo ID
        :param mode: Mode ID (0, 1, 2 or 3 - Cf register values)
          - 0: Position Mode
          - 1: Constant speed mode
          - 2: PWM Mode
          - 3: Step servo mode

        :return: Tuple of (success, error_code). True if successfully set, None in case of error.
        """
        logger.debug(f"Setting mode for servo {servo_id} to {mode}")
        txpacket = [mode]
        comm, error = self.write_tx_rx(servo_id, STS_MODE, len(txpacket), txpacket)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} mode set successfully")
            return True, error
        else:
            logger.warning(
                f"Failed to set mode for servo {servo_id}: comm={comm}, error={error}"
            )
            return None, error

    def set_position_correction(
        self, servo_id: int, correction: int
    ) -> Tuple[Optional[bool], int]:
        """
        Add a position correction to the servo.

        :param servo_id: Servo ID
        :param correction: Correction in steps (can be negative)

        :return: Tuple of (success, error_code). True if successfully set, None in case of error.
        """
        logger.debug(
            f"Setting position correction for servo {servo_id} to {correction}"
        )
        corr = abs(correction)
        if corr > MAX_CORRECTION:
            logger.warning(
                f"Correction value {corr} exceeds maximum {MAX_CORRECTION}, clamping"
            )
            corr = MAX_CORRECTION

        txpacket = [self.sts_lobyte(corr), self.sts_hibyte(corr)]

        if correction < 0:
            txpacket[1] |= 1 << 3

        comm, error = self.write_tx_rx(servo_id, STS_OFS_L, len(txpacket), txpacket)
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} position correction set successfully")
            return True, error
        else:
            logger.warning(
                f"Failed to set position correction for servo {servo_id}: comm={comm}, error={error}"
            )
            return None, error

    def write_position(self, servo_id: int, position: int) -> Optional[bool]:
        """
        Write the target position for the servo to move to.

        :param servo_id: Servo ID
        :param position: Target position

        :return: True if successfully written, None in case of error.
        """
        logger.debug(f"Writing target position {position} to servo {servo_id}")
        txpacket = [self.sts_lobyte(position), self.sts_hibyte(position)]
        comm, error = self.write_tx_rx(
            servo_id, STS_GOAL_POSITION_L, len(txpacket), txpacket
        )
        if comm == 0 and error == 0:
            logger.debug(f"Servo {servo_id} target position written successfully")
            return True
        else:
            logger.warning(
                f"Failed to write position for servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    # ============================================================================
    # TORQUE/POWER CONTROL METHODS
    # ============================================================================

    def enable_torque(self, servo_id: int) -> Tuple[Optional[bool], int]:
        """
        Enable torque on the servo (start the servo).

        :param servo_id: Servo ID

        :return: Tuple of (success, error_code). True if successfully enabled, None in case of error.
        """
        logger.debug(f"Enabling torque for servo {servo_id}")
        txpacket = [1]
        comm, error = self.write_tx_rx(
            servo_id, STS_TORQUE_ENABLE, len(txpacket), txpacket
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.info(f"Servo {servo_id} torque enabled")
            return True, error
        else:
            logger.warning(
                f"Failed to enable torque for servo {servo_id}: comm={comm}, error={error}"
            )
            return None, error

    def disable_torque(self, servo_id: int) -> Optional[bool]:
        """
        Disable torque on the servo (stop the servo).

        :param servo_id: Servo ID

        :return: True if successfully disabled, None in case of error.
        """
        logger.debug(f"Disabling torque for servo {servo_id}")
        txpacket = [0]
        comm, error = self.write_tx_rx(
            servo_id, STS_TORQUE_ENABLE, len(txpacket), txpacket
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.info(f"Servo {servo_id} torque disabled")
            return True
        else:
            logger.warning(
                f"Failed to disable torque for servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    def set_torque_neutral(self, servo_id: int) -> Optional[bool]:
        """
        Set the servo to neutral position (torque = 128, defines the 2048 position).

        :param servo_id: Servo ID

        :return: True if successfully set, None in case of error.
        """
        logger.debug(f"Setting servo {servo_id} to torque neutral")
        txpacket = [128]
        comm, error = self.write_tx_rx(
            servo_id, STS_TORQUE_ENABLE, len(txpacket), txpacket
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} set to torque neutral")
            return True
        else:
            logger.warning(
                f"Failed to set torque neutral for servo {servo_id}: comm={comm}, error={error}"
            )
            return None

    # ============================================================================
    # MOVEMENT CONTROL METHODS
    # ============================================================================

    def move_to(
        self,
        servo_id: int,
        position: int,
        speed: int = 2400,
        acceleration: int = 50,
        wait: bool = False,
    ) -> Optional[bool]:
        """
        Move the servo to a pre-defined position.

        :param servo_id: Servo ID
        :param position: Target position of the servo
        :param speed: Movement speed in step/s (default: 2400)
        :param acceleration: Acceleration in step/s² (default: 50)
        :param wait: Wait for position to be reached before returning (default: False)

        :return: True on success, None in case of error.
        """
        logger.info(
            f"Moving servo {servo_id} to position {position} (speed={speed}, accel={acceleration}, wait={wait})"
        )

        res_mode = self.set_mode(servo_id, 0)
        res_acc = self.set_acceleration(servo_id, acceleration)
        res_speed = self.set_speed(servo_id, speed)

        if res_acc is None or res_speed is None or res_mode is None:
            logger.error(f"Failed to configure servo {servo_id} for movement")
            return None

        curr_pos = self.read_position(servo_id)

        res_pos = self.write_position(servo_id, position)
        if res_pos is None:
            logger.error(f"Failed to write target position for servo {servo_id}")
            return None

        if wait:
            if position is None:
                logger.warning(
                    f"Cannot wait for movement completion: target position is None"
                )
                return None
            else:
                distance = abs(position - curr_pos)
                logger.debug(f"Waiting for servo {servo_id} to travel {distance} steps")

            time_to_speed = speed / (acceleration * 100)

            distance_acc = 0.5 * (acceleration * 100) * time_to_speed**2

            if distance_acc >= distance:
                time_wait = math.sqrt(2 * distance / acceleration)
            else:
                remain_distance = distance - distance_acc
                time_wait = time_to_speed + (remain_distance / speed)

            logger.debug(f"Calculated wait time: {time_wait:.3f}s")
            time.sleep(time_wait)
            logger.debug(f"Servo {servo_id} movement should be complete")

        logger.info(f"Servo {servo_id} move command completed successfully")
        return True

    def rotate(self, servo_id: int, speed: int) -> Tuple[Optional[bool], int]:
        """
        Start rotating the servo in constant speed mode.

        :param servo_id: Servo ID
        :param speed: Servo speed (can be negative for counter-clockwise rotation)

        :return: Tuple of (success, error_code). True if successfully started, None in case of error.
        """
        direction = "counter-clockwise" if speed < 0 else "clockwise"
        logger.info(f"Rotating servo {servo_id} at speed {speed} ({direction})")

        self.set_mode(servo_id, 1)

        abs_speed = abs(speed)
        if abs_speed > MAX_SPEED:
            logger.warning(f"Speed {abs_speed} exceeds maximum {MAX_SPEED}, clamping")
            abs_speed = MAX_SPEED

        txpacket = [self.sts_lobyte(abs_speed), self.sts_hibyte(abs_speed)]

        if speed < 0:
            txpacket[1] |= 1 << 7

        comm, error = self.write_tx_rx(
            servo_id, STS_GOAL_SPEED_L, len(txpacket), txpacket
        )
        if comm == COMM_SUCCESS and error == 0:
            logger.debug(f"Servo {servo_id} rotation started successfully")
            return True, error
        else:
            logger.warning(
                f"Failed to start rotation for servo {servo_id}: comm={comm}, error={error}"
            )
            return None, error

    def get_blocking_position(self, servo_id: int) -> Optional[int]:
        """
        Get the next blocking position when the servo reaches its limit.
        Useful for calibration and finding mechanical limits.

        :param servo_id: Servo ID

        :return: Blocking position, None in case of error.
        """
        logger.info(f"Getting blocking position for servo {servo_id}")

        stop_matches = 0
        while True:
            moving = self.is_moving(servo_id)
            if moving is None:
                logger.error(f"Failed to check movement status for servo {servo_id}")
                self.set_mode(servo_id, 0)
                self.disable_torque(servo_id)
                return None

            if not moving:
                position = self.read_position(servo_id)
                self.set_mode(servo_id, 0)
                self.disable_torque(servo_id)

                if position is None:
                    logger.error(
                        f"Failed to read blocking position for servo {servo_id}"
                    )
                    return None
                else:
                    stop_matches += 1
                    if stop_matches > 4:
                        logger.info(
                            f"Servo {servo_id} blocking position found: {position}"
                        )
                        return position
            else:
                stop_matches = 0

            time.sleep(0.02)

    # ============================================================================
    # CALIBRATION METHODS
    # ============================================================================

    def calibrate_servo(self, servo_id: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Calibrate a servo by finding its min and max positions, then setting the 0 position.

        WARNING: Only use for servos with at least one blocking position.
                 Never use this for free rotation servos.

        :param servo_id: Servo ID

        :return: Tuple of (min_position, max_position), or (None, None) in case of error.
        """

        if self.set_position_correction(servo_id, 0) is None:
            return None, None

        time.sleep(0.5)

        self.set_acceleration(servo_id, 100)
        self.rotate(servo_id, -250)
        time.sleep(0.5)

        min_position = self.get_blocking_position(servo_id)

        self.rotate(servo_id, 250)
        time.sleep(0.5)

        max_position = self.get_blocking_position(servo_id)

        if min_position is not None and max_position is not None:

            # Now, set the middle of the path to 2048
            if min_position >= max_position:
                distance = int(((MAX_POSITION - min_position + max_position) / 2))
            else:
                distance = int(((max_position - min_position) / 2))

            if min_position > int(MAX_POSITION / 2):
                corr = min_position - MAX_POSITION - 1
            else:
                corr = min_position

            if self.set_position_correction(servo_id, corr) is not None:
                min_position = 0
                max_position = distance * 2
                time.sleep(0.5)

                self.move_to(servo_id, distance)

        return min_position, max_position

    # ============================================================================
    # EEPROM MANAGEMENT METHODS
    # ============================================================================

    def lock_eeprom(self, servo_id: int) -> int:
        """
        Lock the servo EEPROM to prevent accidental configuration changes.

        :param servo_id: Servo ID

        :return: 0 in case of success
        """
        return self.write_tx_1byte(servo_id, STS_LOCK, 1)

    def unlock_eeprom(self, servo_id: int) -> int:
        """
        Unlock the servo EEPROM to allow configuration changes.

        :param servo_id: Servo ID

        :return: 0 in case of success
        """
        return self.write_tx_1byte(servo_id, STS_LOCK, 0)

    def change_servo_id(self, servo_id: int, new_id: int) -> Optional[str]:
        """
        Change the ID of a servo.

        :param servo_id: Current ID of the servo (1 for a brand new servo)
        :param new_id: New ID for the servo (0-253)

        :return: None if successful, otherwise an error message string
        """
        if isinstance(new_id, int) and 0 <= new_id <= 253:
            if not self.ping_servo(servo_id):
                return f"Could not find servo: {servo_id}"

            if self.unlock_eeprom(servo_id) != COMM_SUCCESS:
                return "Could not unlock EEPROM"

            if self.write_tx_1byte(servo_id, STS_ID, new_id) != COMM_SUCCESS:
                return "Could not change servo ID"

            self.lock_eeprom(servo_id)
            return None
        else:
            return "new_id must be an integer between 0 and 253"

    # ============================================================================
    # DEPRECATED API - BACKWARD COMPATIBILITY ALIASES
    # ============================================================================

    def PingServo(self, sts_id: int) -> bool:
        """
        DEPRECATED: Use ping_servo() instead.
        """
        warnings.warn(
            "PingServo() is deprecated, use ping_servo() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.ping_servo(sts_id)

    def ListServos(self) -> List[int]:
        """
        DEPRECATED: Use scan_servos() instead.
        """
        warnings.warn(
            "ListServos() is deprecated, use scan_servos() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.scan_servos()

    def ReadLoad(self, sts_id: int) -> Optional[float]:
        """
        DEPRECATED: Use read_load() instead.
        """
        warnings.warn(
            "ReadLoad() is deprecated, use read_load() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_load(sts_id)

    def ReadVoltage(self, sts_id: int) -> Optional[float]:
        """
        DEPRECATED: Use read_voltage() instead.
        """
        warnings.warn(
            "ReadVoltage() is deprecated, use read_voltage() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_voltage(sts_id)

    def ReadCurrent(self, sts_id: int) -> Optional[float]:
        """
        DEPRECATED: Use read_current() instead.
        """
        warnings.warn(
            "ReadCurrent() is deprecated, use read_current() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_current(sts_id)

    def ReadTemperature(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use read_temperature() instead.
        """
        warnings.warn(
            "ReadTemperature() is deprecated, use read_temperature() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_temperature(sts_id)

    def ReadAcceleration(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use read_acceleration() instead.
        """
        warnings.warn(
            "ReadAcceleration() is deprecated, use read_acceleration() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_acceleration(sts_id)

    def ReadMode(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use read_mode() instead.
        """
        warnings.warn(
            "ReadMode() is deprecated, use read_mode() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_mode(sts_id)

    def ReadCorrection(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use read_position_correction() instead.
        """
        warnings.warn(
            "ReadCorrection() is deprecated, use read_position_correction() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_position_correction(sts_id)

    def IsMoving(self, sts_id: int) -> Optional[bool]:
        """
        DEPRECATED: Use is_moving() instead.
        """
        warnings.warn(
            "IsMoving() is deprecated, use is_moving() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.is_moving(sts_id)

    def SetAcceleration(self, sts_id: int, acc: int) -> Optional[bool]:
        """
        DEPRECATED: Use set_acceleration() instead.
        """
        warnings.warn(
            "SetAcceleration() is deprecated, use set_acceleration() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_acceleration(sts_id, acc)

    def SetSpeed(self, sts_id: int, speed: int) -> Optional[bool]:
        """
        DEPRECATED: Use set_speed() instead.
        """
        warnings.warn(
            "SetSpeed() is deprecated, use set_speed() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_speed(sts_id, speed)

    def StopServo(self, sts_id: int) -> Optional[bool]:
        """
        DEPRECATED: Use disable_torque() instead.
        """
        warnings.warn(
            "StopServo() is deprecated, use disable_torque() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.disable_torque(sts_id)

    def StartServo(self, sts_id: int) -> Tuple[Optional[bool], int]:
        """
        DEPRECATED: Use enable_torque() instead.
        """
        warnings.warn(
            "StartServo() is deprecated, use enable_torque() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.enable_torque(sts_id)

    def SetMode(self, sts_id: int, mode: int) -> Tuple[Optional[bool], int]:
        """
        DEPRECATED: Use set_mode() instead.
        """
        warnings.warn(
            "SetMode() is deprecated, use set_mode() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_mode(sts_id, mode)

    def CorrectPosition(
        self, sts_id: int, correction: int
    ) -> Tuple[Optional[bool], int]:
        """
        DEPRECATED: Use set_position_correction() instead.
        """
        warnings.warn(
            "CorrectPosition() is deprecated, use set_position_correction() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_position_correction(sts_id, correction)

    def Rotate(self, sts_id: int, speed: int) -> Tuple[Optional[bool], int]:
        """
        DEPRECATED: Use rotate() instead.
        """
        warnings.warn(
            "Rotate() is deprecated, use rotate() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.rotate(sts_id, speed)

    def getBlockPosition(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use get_blocking_position() instead.
        """
        warnings.warn(
            "getBlockPosition() is deprecated, use get_blocking_position() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_blocking_position(sts_id)

    def DefineMiddle(self, sts_id: int) -> Optional[bool]:
        """
        DEPRECATED: Use set_torque_neutral() instead.
        """
        warnings.warn(
            "DefineMiddle() is deprecated, use set_torque_neutral() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_torque_neutral(sts_id)

    def TareServo(self, sts_id: int) -> Tuple[Optional[int], Optional[int]]:
        """
        DEPRECATED: Use calibrate_servo() instead.
        """
        warnings.warn(
            "TareServo() is deprecated, use calibrate_servo() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.calibrate_servo(sts_id)

    def MoveTo(
        self,
        sts_id: int,
        position: int,
        speed: int = 2400,
        acc: int = 50,
        wait: bool = False,
    ) -> Optional[bool]:
        """
        DEPRECATED: Use move_to() instead.
        """
        warnings.warn(
            "MoveTo() is deprecated, use move_to() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.move_to(sts_id, position, speed, acc, wait)

    def WritePosition(self, sts_id: int, position: int) -> Optional[bool]:
        """
        DEPRECATED: Use write_position() instead.
        """
        warnings.warn(
            "WritePosition() is deprecated, use write_position() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.write_position(sts_id, position)

    def ReadStatus(self, sts_id: int) -> Optional[dict]:
        """
        DEPRECATED: Use read_status() instead.
        """
        warnings.warn(
            "ReadStatus() is deprecated, use read_status() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_status(sts_id)

    def ReadPosition(self, sts_id: int) -> Optional[int]:
        """
        DEPRECATED: Use read_position() instead.
        """
        warnings.warn(
            "ReadPosition() is deprecated, use read_position() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_position(sts_id)

    def ReadSpeed(self, sts_id: int) -> Tuple[int, int, int]:
        """
        DEPRECATED: Use read_speed() instead.
        """
        warnings.warn(
            "ReadSpeed() is deprecated, use read_speed() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.read_speed(sts_id)

    def LockEprom(self, sts_id: int) -> int:
        """
        DEPRECATED: Use lock_eeprom() instead.
        """
        warnings.warn(
            "LockEprom() is deprecated, use lock_eeprom() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.lock_eeprom(sts_id)

    def UnLockEprom(self, sts_id: int) -> int:
        """
        DEPRECATED: Use unlock_eeprom() instead.
        """
        warnings.warn(
            "UnLockEprom() is deprecated, use unlock_eeprom() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.unlock_eeprom(sts_id)

    def ChangeId(self, sts_id: int, new_id: int) -> Optional[str]:
        """
        DEPRECATED: Use change_servo_id() instead.
        """
        warnings.warn(
            "ChangeId() is deprecated, use change_servo_id() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.change_servo_id(sts_id, new_id)
