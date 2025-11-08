
# ST3215 Servo Motor Python Module

This Python module provides a high-level API to communicate and control ST3215 servo motors via serial communication. It wraps around a low-level protocol to easily manage motion, configuration, and diagnostics of ST3215 devices using `pyserial` and custom STS protocol definitions.

## Features

- Auto-detection of connected servos
- Read servo telemetry: position, speed, temperature, voltage, current, load
- Write target position, speed, and acceleration
- Rotate continuously in either direction
- Define and correct middle position
- EEPROM locking and ID reconfiguration
- Configurable logging support


## Example Usage

```python
from st3215 import ST3215

# Initialize the controller
servo = ST3215('/dev/ttyUSB0')

# Scan for connected servos
ids = servo.scan_servos()
if ids:
    # Move the first servo to position 2048
    servo.move_to(ids[0], 2048)
```

## Logging Configuration

You can configure logging to monitor the library's operations:

```python
import st3215
import logging

# Enable debug logging
st3215.configure_logging(level=logging.DEBUG)

# Or use INFO level for less verbose output
st3215.configure_logging(level=logging.INFO)

# You can also provide a custom handler
handler = logging.FileHandler('st3215.log')
st3215.configure_logging(level=logging.DEBUG, handler=handler)
```

---

## Full API Documentation

### Discovery & Communication

#### `ping_servo(servo_id)`
Check if a servo is responding.

- **Parameters**: `servo_id` (int) – Servo ID
- **Returns**: `True` if successful, `False` otherwise
- **Example**:
```python
servo.ping_servo(1)
```

---

#### `scan_servos()`
Scan the bus and return a list of all responsive servos.

- **Returns**: `List[int]` of servo IDs
- **Example**:
```python
ids = servo.scan_servos()
print(f"Found servos: {ids}")
```

---

### Read Sensor Methods (Telemetry)

#### `read_load(servo_id)`
Get the motor load in %.

- **Parameters**: `servo_id` (int)
- **Returns**: `float` (percentage) or `None` in case of error
- **Example**:
```python
load = servo.read_load(1)
print(f"Load: {load}%")
```

---

#### `read_voltage(servo_id)`
Read voltage in volts.

- **Parameters**: `servo_id` (int)
- **Returns**: `float` (volts) or `None` in case of error
- **Example**:
```python
voltage = servo.read_voltage(1)
print(f"Voltage: {voltage}V")
```

---

#### `read_current(servo_id)`
Get current in mA.

- **Parameters**: `servo_id` (int)
- **Returns**: `float` (milliamperes) or `None` in case of error
- **Example**:
```python
current = servo.read_current(1)
print(f"Current: {current}mA")
```

---

#### `read_temperature(servo_id)`
Read current temperature in °C.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (degrees Celsius) or `None` in case of error
- **Example**:
```python
temp = servo.read_temperature(1)
print(f"Temperature: {temp}°C")
```

---

#### `read_position(servo_id)`
Read current position.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (position in steps) or `None` in case of error
- **Example**:
```python
position = servo.read_position(1)
print(f"Position: {position}")
```

---

#### `read_speed(servo_id)`
Get current speed.

- **Parameters**: `servo_id` (int)
- **Returns**: `Tuple[int, int, int]` (speed, comm_result, error)
- **Example**:
```python
speed, comm, error = servo.read_speed(1)
if comm == 0 and error == 0:
    print(f"Speed: {speed} step/s")
```

---

#### `read_status(servo_id)`
Read the sensor status of the servo.

Returns a dict with sensor status: `{'Voltage': True, 'Sensor': True, 'Temperature': True, 'Current': True, 'Angle': True, 'Overload': True}`

- **Parameters**: `servo_id` (int)
- **Returns**: `dict` or `None` in case of error
- **Example**:
```python
status = servo.read_status(1)
if status:
    print(f"Status: {status}")
```

---

#### `is_moving(servo_id)`
Check if the servo is moving.

- **Parameters**: `servo_id` (int)
- **Returns**: `bool` or `None` in case of error
- **Example**:
```python
if servo.is_moving(1):
    print("Servo is moving")
```

---

### Read Configuration Methods

#### `read_acceleration(servo_id)`
Read current acceleration value in step/s².

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (acceleration value) or `None` in case of error
- **Example**:
```python
acc = servo.read_acceleration(1)
print(f"Acceleration: {acc} step/s²")
```

---

#### `read_mode(servo_id)`
Get current operational mode.

Mode values:
- 0: position servo mode 
- 1: motor constant speed mode
- 2: PWM open-loop speed regulation mode
- 3: step servo mode

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (0-3) or `None` in case of error
- **Example**:
```python
mode = servo.read_mode(1)
```

---

#### `read_position_correction(servo_id)`
Read position correction value in steps.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (correction value) or `None` in case of error
- **Example**:
```python
correction = servo.read_position_correction(1)
```

---

### Write Configuration Methods

#### `set_acceleration(servo_id, acceleration)`
Set acceleration value in step/s².

- **Parameters**:
  - `servo_id` (int)
  - `acceleration` (int, 0–254) – Unit: 100 step/s²
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
servo.set_acceleration(1, 100)
```

---

#### `set_speed(servo_id, speed)`
Set servo speed in step/s.

- **Parameters**:
  - `servo_id` (int)
  - `speed` (int, 0-3400) – Unit: step/s
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
servo.set_speed(1, 3000)
```

---

#### `set_mode(servo_id, mode)`
Set operational mode.

Mode values:
- 0: position servo mode 
- 1: motor constant speed mode
- 2: PWM open-loop speed regulation mode
- 3: step servo mode

- **Parameters**:
  - `servo_id` (int)
  - `mode` (int, 0–3)
- **Returns**: `Tuple[bool, int]` (success, error_code). True if successfully set, None in case of error.
- **Example**:
```python
success, error = servo.set_mode(1, 0)
```

---

#### `set_position_correction(servo_id, correction)`
Apply a position correction in steps.

- **Parameters**:
  - `servo_id` (int)
  - `correction` (int, can be negative)
- **Returns**: `Tuple[bool, int]` (success, error_code). True if successfully set, None in case of error.
- **Example**:
```python
success, error = servo.set_position_correction(1, -100)
```

---

#### `write_position(servo_id, position)`
Direct position write (low-level command).

- **Parameters**:
  - `servo_id` (int)
  - `position` (int)
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
servo.write_position(1, 2048)
```

---

### Torque/Power Control Methods

#### `enable_torque(servo_id)`
Enable torque on the servo (start the servo).

- **Parameters**: `servo_id` (int)
- **Returns**: `Tuple[bool, int]` (success, error_code). True if successfully enabled, None in case of error.
- **Example**:
```python
success, error = servo.enable_torque(1)
```

---

#### `disable_torque(servo_id)`
Disable torque on the servo (stop the servo).

- **Parameters**: `servo_id` (int)
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
servo.disable_torque(1)
```

---

#### `set_torque_neutral(servo_id)`
Set the servo to neutral position (defines current position as 2048).

- **Parameters**: `servo_id` (int)
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
servo.set_torque_neutral(1)
```

---

### Movement Control Methods

#### `move_to(servo_id, position, speed=2400, acceleration=50, wait=False)`
Move the servo to a pre-defined position.

- **Parameters**:
  - `servo_id` (int)
  - `position` (int) – Target position
  - `speed` (int) – Movement speed in step/s (default: 2400)
  - `acceleration` (int) – Acceleration in step/s² (default: 50)
  - `wait` (bool) – Wait for position to be reached before returning (default: False)
- **Returns**: `True` or `None` in case of error
- **Example**:
```python
# Move to position 2048 with default speed and acceleration
servo.move_to(1, 2048)

# Move with custom speed and wait for completion
servo.move_to(1, 3000, speed=1500, acceleration=100, wait=True)
```

---

#### `rotate(servo_id, speed)`
Rotate in continuous speed mode.

- **Parameters**:
  - `servo_id` (int)
  - `speed` (int, can be negative for counter-clockwise rotation)
- **Returns**: `Tuple[bool, int]` (success, error_code). True if successfully started, None in case of error.
- **Example**:
```python
# Rotate clockwise
success, error = servo.rotate(1, 250)

# Rotate counter-clockwise
success, error = servo.rotate(1, -250)
```

---

#### `get_blocking_position(servo_id)`
Get the next blocking position when the servo reaches its physical limit.
Useful for calibration and finding mechanical limits.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (blocking position) or `None` in case of error
- **Example**:
```python
position = servo.get_blocking_position(1)
```

---

### Calibration Methods

#### `calibrate_servo(servo_id)`
Calibrate a servo by finding its min and max positions, then setting the middle position.

**WARNING**: Only use for servos with at least one blocking position.
Never use this for free rotation servos.

- **Parameters**: `servo_id` (int)
- **Returns**: `Tuple[int, int]` (min_position, max_position) or `(None, None)` in case of error
- **Example**:
```python
min_pos, max_pos = servo.calibrate_servo(1)
if min_pos is not None:
    print(f"Range: {min_pos} to {max_pos}")
```

---

### EEPROM Management Methods

#### `lock_eeprom(servo_id)`
Lock the servo EEPROM to prevent accidental configuration changes.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (0 in case of success)
- **Example**:
```python
result = servo.lock_eeprom(1)
```

---

#### `unlock_eeprom(servo_id)`
Unlock the servo EEPROM to allow configuration changes.

- **Parameters**: `servo_id` (int)
- **Returns**: `int` (0 in case of success)
- **Example**:
```python
result = servo.unlock_eeprom(1)
```

---

#### `change_servo_id(servo_id, new_id)`
Change the ID of a servo.

- **Parameters**:
  - `servo_id` (int) – Current ID of the servo
  - `new_id` (int) – New ID for the servo (0-253)
- **Returns**: `None` if successful, otherwise an error message string
- **Example**:
```python
error = servo.change_servo_id(1, 2)
if error:
    print(f"Error: {error}")
```

---

## Backward Compatibility

The library maintains backward compatibility with the older CamelCase API. All old method names are still available but deprecated:

- `PingServo()` → `ping_servo()`
- `ListServos()` → `scan_servos()`
- `ReadLoad()` → `read_load()`
- `ReadVoltage()` → `read_voltage()`
- `ReadCurrent()` → `read_current()`
- `ReadTemperature()` → `read_temperature()`
- `ReadAcceleration()` → `read_acceleration()`
- `ReadMode()` → `read_mode()`
- `ReadCorrection()` → `read_position_correction()`
- `ReadStatus()` → `read_status()`
- `IsMoving()` → `is_moving()`
- `SetAcceleration()` → `set_acceleration()`
- `SetSpeed()` → `set_speed()`
- `StopServo()` → `disable_torque()`
- `StartServo()` → `enable_torque()`
- `SetMode()` → `set_mode()`
- `CorrectPosition()` → `set_position_correction()`
- `Rotate()` → `rotate()`
- `MoveTo()` → `move_to()`
- `WritePosition()` → `write_position()`
- `ReadPosition()` → `read_position()`
- `ReadSpeed()` → `read_speed()`
- `LockEprom()` → `lock_eeprom()`
- `UnLockEprom()` → `unlock_eeprom()`
- `ChangeId()` → `change_servo_id()`
- `DefineMiddle()` → `set_torque_neutral()`
- `TareServo()` → `calibrate_servo()`
- `getBlockPosition()` → `get_blocking_position()`

**Note**: Using deprecated methods will generate deprecation warnings. Please update your code to use the new snake_case methods.

---

## ST3215 registers

> Bytes are little-endian


| Memory First Address   | Function                                       |   Number of Bytes |   Initial Value | Storage Area   | Permission   | Minimum Value   | Maximum Value   | Unit         | Value Parsing                                                                                                                                                                                                                                                                                                                                                                                   |
|:-----------------------|:-----------------------------------------------|------------------:|----------------:|:---------------|:-------------|:----------------|:----------------|:-------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x0                    | Firmware major version number                  |                 1 |               3 | EPROM          | read only    | -1              | -1              | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 0x1                    | Firmware minor version number                  |                 1 |               7 | EPROM          | read only    | -1              | -1              | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 0x3                    | Servo major version number                     |                 1 |               9 | EPROM          | read only    | -1              | -1              | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 0x4                    | Servo minor version number                     |                 1 |               3 | EPROM          | read only    | -1              | -1              | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 0x5                    | ID                                             |                 1 |               1 | EPROM          | read/write   | 0               | 253             | Baud         | A unique identification code on the bus, with no duplicate ID numbers allowed on the same bus. ID number 254 (0xFE) is the broadcast ID, and broadcasts do not receive response packets.                                                                                                                                                                                                        |
| 0x6                    | Baudrate                                       |                 1 |               0 | EPROM          | read/write   | 0               | 7               | None         | 0-7 respectively represent baud rates as follows:                                                                                                                                                                                                                                                                                                                                               |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400                                                                                                                                                                                                                                                                                                                                    |
| 0x7                    | Return delay                                   |                 1 |               0 | EPROM          | read/write   | 0               | 254             | 2us          | The minimum unit is 2us, and the maximum allowable setting for response delay is 254*2=508us                                                                                                                                                                                                                                                                                                    |
| 0x8                    | Response status level                          |                 1 |               1 | EPROM          | read/write   | 0               | 1               | None         | 0: Except for read and PING instructions, other instructions do not return response packets.                                                                                                                                                                                                                                                                                                    |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1: Return response packets for all instructions                                                                                                                                                                                                                                                                                                                                                 |
| 0x9                    | Minimum angle                                  |                 2 |               0 | EPROM          | read/write   | -32766          | --              | Step         | Set the minimum value limit for the motion range, which should be smaller than the maximum angle limit. When performing multi-turn absolute position control, this value is set to 0.                                                                                                                                                                                                           |
| 0xB                    | Maximum angle                                  |                 2 |            4095 | EPROM          | read/write   | --              | 32767           | Step         | Set the maximum value limit for the motion range, which should be greater than the minimum angle limit. When performing multi-turn absolute position control, this value is set to 0.                                                                                                                                                                                                           |
| 0xD                    | Maximum temperature                            |                 1 |              70 | EPROM          | read/write   | 0               | 100             | °C           | The maximum operating temperature limit, when set to 70, means the maximum temperature is 70 degrees Celsius, with a precision setting of 1 degree Celsius.                                                                                                                                                                                                                                     |
| 0xE                    | Maximum input voltage                          |                 1 |              80 | EPROM          | read/write   | 0               | 254             | 0.1V         | If the maximum input voltage is set to 80, then the maximum operating voltage limit is 8.0V, with a precision setting of 0.1V.                                                                                                                                                                                                                                                                  |
| 0xF                    | Minimum input voltage                          |                 1 |              40 | EPROM          | read/write   | 0               | 254             | 0.1V         | If the minimum input voltage is set to 40, then the minimum operating voltage limit is 4.0V, with a precision setting of 0.1V.                                                                                                                                                                                                                                                                  |
| 0x10                   | Maximum torque                                 |                 2 |            1000 | EPROM          | read/write   | 0               | 1000            | nan          | Set the maximum output torque limit for the servo motor, where 1000 corresponds to 100% of the locked-rotor torque. Assign this value to address 48 upon power-up as the torque limit.                                                                                                                                                                                                          |
| 0x12                   | Phase                                          |                 1 |              12 | EPROM          | read/write   | 0               | 254             | None         | Special function byte, do not modify unless there are specific requirements. Please refer to the special byte bit analysis for further details.                                                                                                                                                                                                                                                 |
| 0x13                   | Unloading conditions                           |                 1 |              44 | EPROM          | read/write   | 0               | 254             | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 set corresponding bit to 1 to enable the corresponding protection.                                                                                                                                                                                                                                                                                              |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload set corresponding bit to 0 to disable the corresponding protection                                                                                                                                                                                                                                                                            |
| 0x14                   | LED alarm conditions                           |                 1 |              47 | EPROM          | read/write   | 0               | 254             | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 set the corresponding bit to 1 to enable flashing  LED.                                                                                                                                                                                                                                                                                                         |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload set corresponding bit to 0 to disable the corresponding protection                                                                                                                                                                                                                                                                            |
| 0x15                   | Position loop P (Proportional) coefficient     |                 1 |              32 | EPROM          | read/write   | 0               | 254             | None         | Proportional coefficient of control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x16                   | Position loop D (Differential) coefficient     |                 1 |              32 | EPROM          | read/write   | 0               | 254             | None         | Differential coefficient of control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x17                   | Position loop I (Integral) coefficient         |                 1 |               0 | EPROM          | read/write   | 0               | 254             | None         | Integral coefficient of the control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x18                   | Minimum starting force                         |                 2 |              16 | EPROM          | read/write   | 0               | 1000            | nan          | Set the minimum output startup torque for the servo, where 1000 corresponds to 100% of the locked-rotor torque.                                                                                                                                                                                                                                                                                 |
| 0x1A                   | Clockwise insensitive zone                     |                 1 |               1 | EPROM          | read/write   | 0               | 32              | Step         | The minimum unit is one minimum resolution angle.                                                                                                                                                                                                                                                                                                                                               |
| 0x1B                   | Anti-clockwise insensitive zone                |                 1 |               1 | EPROM          | read/write   | 0               | 32              | Step         | The minimum unit is a minimum resolution angle.                                                                                                                                                                                                                                                                                                                                                 |
| 0x1C                   | Protection current                             |                 2 |             500 | EPROM          | read/write   | 0               | 511             | 6.5mA        | The maximum settable current is 500 * 6.5mA= 3250mA.                                                                                                                                                                                                                                                                                                                                            |
| 0x1E                   | Angle resolution                               |                 1 |               1 | EPROM          | read/write   | 1               | 3               | None         | For the amplification factor of the minimum resolution angle (degree/step) of the sensor, modifying this value can expand the number of control range. When performing the multi-turn control, you need to modify the parameter at address 0x12 by setting BIT4 to 1. This modification will result in the current position feedback value being adjusted to reflect the larger angle feedback. |
| 0x1F                   | Position correction                            |                 2 |               0 | EPROM          | read/write   | -2047           | 2047            | Step         | BIT11 is the direction bit, indicating the positive and negative direction, and other bits can indicate the range of 0-2047 steps.                                                                                                                                                                                                                                                              |
| 0x21                   | Operation mode                                 |                 1 |               0 | EPROM          | read/write   | 0               | 3               | None         | 0: position servo mode                                                                                                                                                                                                                                                                                                                                                                          |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1: motor constant speed mode, controlled by parameter 0x2E running speed parameter, the highest bit BIT15 is direction bit.                                                                                                                                                                                                                                                                     |
|                        |                                                |                   |                 |                |              |                 |                 |              | 2: PWM open-loop speed regulation mode, controlled by parameter 0x2Cthe  running time parameter, BIT10 is direction bit                                                                                                                                                                                                                                                                         |
|                        |                                                |                   |                 |                |              |                 |                 |              | 3: step servo mode, and the target position of parameter 0x2A is used to indicate the number of steps, and the highest bit BIT15 is the direction bit. When working                                                                                                                                                                                                                             |
|                        |                                                |                   |                 |                |              |                 |                 |              | In mode 3, the minimum and maximum angle limits of 0x9 and 0xB must be set to 0. Otherwise, it is impossible to step indefinitely.                                                                                                                                                                                                                                                              |
| 0x22                   | Protection torque                              |                 1 |              20 | EPROM          | read/write   | 0               | 100             | nan          | Output torque after entering overload protection. If 20 is set, it means 20% of the maximum torque.                                                                                                                                                                                                                                                                                             |
| 0x23                   | Protection time                                |                 1 |             200 | EPROM          | read/write   | 0               | 254             | 10ms         | The duration for which the current load output exceeds the overload torque and remains is represented by a value, such as 200, which indicates 2 seconds. The maximum value that can be set is 2.5 seconds.                                                                                                                                                                                     |
| 0x24                   | Overload torque                                |                 1 |              80 | EPROM          | read/write   | 0               | 100             | nan          | The maximum torque threshold for starting the overload protection time countdown can be represented by a value, such as 80, indicating 80% of the maximum torque.                                                                                                                                                                                                                               |
| 0x25                   | Speed closed-loop proportional (P) coefficient |                 1 |              10 | EPROM          | read/write   | 0               | 100             | None         | Proportional coefficient of speed loop in motor constant speed mode (mode 1)                                                                                                                                                                                                                                                                                                                    |
| 0x26                   | Overcurrent protection time                    |                 1 |             200 | EPROM          | read/write   | 0               | 254             | 10ms         | The maximum setting is 254 * 10ms = 2540ms.                                                                                                                                                                                                                                                                                                                                                     |
| 0x27                   | Velocity closed-loop integral (I) coefficient  |                 1 |              10 | EPROM          | read/write   | 0               | 254             | 1/10         | In the motor constant speed mode (mode 1), the speed loop integral coefficient (change note: the speed closed loop I integral coefficient is reduced by 10 times compared with version 3.6).                                                                                                                                                                                                    |
| 0x28                   | Torque switch                                  |                 1 |               0 | SRAM           | read/write   | 0               | 128             | None         | Write 0: disable the torque output; Write 1: enable the torque output; Write 128: Arbitrary current position correction to 2048.                                                                                                                                                                                                                                                                |
| 0x29                   | Acceleration                                   |                 1 |               0 | SRAM           | read/write   | 0               | 254             | 100 step/s^2 | If set to 10, it corresponds to an acceleration and deceleration rate of 1000 steps per second squared.                                                                                                                                                                                                                                                                                         |
| 0x2A                   | Target location                                |                 2 |               0 | SRAM           | read/write   | -30719          | 30719           | Step         | Each step corresponds to the minimum resolution angle, and it is used in absolute position control mode. The maximum number of steps corresponds to the maximum effective angle.                                                                                                                                                                                                                |
| 0x2C                   | Operation time                                 |                 2 |               0 | SRAM           | read/write   | 0               | 1000            | nan          | In the PWM open-loop speed control mode, the value range is from 50 to 1000, and BIT10 serves as the direction bit.                                                                                                                                                                                                                                                                             |
| 0x2E                   | Operation speed                                |                 2 |               0 | SRAM           | read/write   | 0               | 3400            | step/s       | Number of steps per unit time (per second), 50 steps per second = 0.732 RPM (revolutions per minute)                                                                                                                                                                                                                                                                                            |
| 0x30                   | Torque limit                                   |                 2 |            1000 | SRAM           | read/write   | 0               | 1000            | nan          | The initial value of power-on will be assigned by the maximum torque (0x10), which can be modified by the user to control the output of the maximum torque.                                                                                                                                                                                                                                     |
| 0x37                   | Lock flag                                      |                 1 |               0 | SRAM           | read/write   | 0               | 1               | None         | Writing 0: Disables the write lock, allowing values written to the EPROM address to be saved even after power loss.                                                                                                                                                                                                                                                                             |
|                        |                                                |                   |                 |                |              |                 |                 |              | Writing 1: Enables the write lock, preventing values written to the EPROM address from being saved after power loss.                                                                                                                                                                                                                                                                            |
| 0x38                   | Current location                               |                 2 |               0 | SRAM           | read only    | -1              | -1              | Step         | Feedback the number of steps in the current position, each step is a minimum resolution angle; Absolute position control mode, the maximum value corresponds to the maximum effective angle.                                                                                                                                                                                                    |
| 0x3A                   | Current speed                                  |                 2 |               0 | SRAM           | read only    | -1              | -1              | step/s       | Feedback the current speed of motor rotation and the number of steps in unit time (per second).                                                                                                                                                                                                                                                                                                 |
| 0x3C                   | Current load                                   |                 2 |               0 | SRAM           | read only    | -1              | -1              | nan          | The voltage duty cycle of the current control output driving motor.                                                                                                                                                                                                                                                                                                                             |
| 0x3E                   | Current voltage                                |                 1 |               0 | SRAM           | read only    | -1              | -1              | 0.1V         | Current servo operation voltage                                                                                                                                                                                                                                                                                                                                                                 |
| 0x3F                   | Current temperature                            |                 1 |               0 | SRAM           | read only    | -1              | -1              | °C           | Current servo internal operating temperature                                                                                                                                                                                                                                                                                                                                                    |
| 0x40                   | Asynchronous write flag                        |                 1 |               0 | SRAM           | read only    | -1              | -1              | None         | The flag bit for using asynchronous write instructions                                                                                                                                                                                                                                                                                                                                          |
| 0x41                   | Servo status                                   |                 1 |               0 | SRAM           | read only    | -1              | -1              | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 the corresponding bit is set to 1 to indicate that the corresponding error occurs,                                                                                                                                                                                                                                                                              |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload the corresponding bit is set to 0 to indicate that there is no corresponding error.                                                                                                                                                                                                                                                           |
| 0x42                   | Move flag                                      |                 1 |               0 | SRAM           | read only    | -1              | -1              | None         | The sign of the servo is 1 when it is moving, and 0 when it is stopped.                                                                                                                                                                                                                                                                                                                         |
| 0x45                   | Current current                                |                 2 |               0 | SRAM           | read only    | -1              | -1              | 6.5mA        | The maximum measurable current is 500 * 6.5mA= 3250mA.                                                                                                                                                                                                                                                                                                                                          |
