
# ST3215 Servo Motor Python Module

This Python module provides a high-level API to communicate and control ST3215 servo motors via serial communication. It wraps around a low-level protocol to easily manage motion, configuration, and diagnostics of ST3215 devices using `pyserial` and custom STS protocol definitions.

## Features

- Auto-detection of connected servos
- Read servo telemetry: position, speed, temperature, voltage, current, load
- Write target position, speed, and acceleration
- Rotate continuously in either direction
- Define and correct middle position
- EEPROM locking and ID reconfiguration


## Example Usage

```python
from st3215 import ST3215

servo = ST3215('/dev/ttyUSB0')
ids = servo.ListServos()
if ids:
    servo.MoveTo(ids[0], 2048)
```

---

## Full API Documentation

### `PingServo(sts_id)`
Check if the servo is responding.

- **Parameters**: `sts_id` (int) – Servo ID
- **Returns**: `True` if successful, `False` otherwise
- **Example**:
```python
servo.PingServo(1)
```

---

### `ListServos()`
Scan and return a list of all responsive servos.

- **Returns**: `List[int]` of servo IDs
- **Example**:
```python
servo.ListServos()
```

---

### `ReadLoad(sts_id)`
Get the motor load in %.

- **Parameters**: `sts_id` (int)
- **Returns**: `float` or `None`
- **Example**:
```python
servo.ReadLoad(1)
```

---

### `ReadVoltage(sts_id)`
Read voltage in volts.

- **Parameters**: `sts_id` (int)
- **Returns**: `float` or `None`
- **Example**:
```python
servo.ReadVoltage(1)
```

---

### `ReadCurrent(sts_id)`
Get current in mA.

- **Parameters**: `sts_id` (int)
- **Returns**: `float` or `None`
- **Example**:
```python
servo.ReadCurrent(1)
```

---

### `ReadTemperature(sts_id)`
Read current temperature.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
servo.ReadTemperature(1)
```

---

### `ReadAccelaration(sts_id)`
Read current acceleration setting.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
servo.ReadAccelaration(1)
```

---

### `ReadMode(sts_id)`
Get current mode.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
servo.ReadMode(1)
```

---

### `ReadCorrection(sts_id)`
Read position correction value.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
servo.ReadCorrection(1)
```

---

### `IsMoving(sts_id)`
Check if the servo is moving.

- **Parameters**: `sts_id` (int)
- **Returns**: `bool` or `None`
- **Example**:
```python
servo.IsMoving(1)
```

---

### `SetAcceleration(sts_id, acc)`
Set acceleration value.

- **Parameters**:
  - `sts_id` (int)
  - `acc` (int, 0–254)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.SetAcceleration(1, 100)
```

---

### `SetSpeed(sts_id, speed)`
Set servo speed.

- **Parameters**:
  - `sts_id` (int)
  - `speed` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.SetSpeed(1, 3000)
```

---

### `StopServo(sts_id)`
Disable torque.

- **Parameters**: `sts_id` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.StopServo(1)
```

---

### `StartServo(sts_id)`
Enable torque.

- **Parameters**: `sts_id` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.StartServo(1)
```

---

### `SetMode(sts_id, mode)`
Set operational mode.

- **Parameters**:
  - `sts_id` (int)
  - `mode` (0–3)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.SetMode(1, 0)
```

---

### `CorrectPosition(sts_id, correction)`
Apply a position correction.

- **Parameters**:
  - `sts_id` (int)
  - `correction` (int, can be negative)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.CorrectPosition(1, -100)
```

---

### `Rotate(sts_id, speed)`
Rotate in continuous mode.

- **Parameters**:
  - `sts_id` (int)
  - `speed` (int, can be negative)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.Rotate(1, 250)
```

---

### `MoveTo(sts_id, position, speed=2400, acc=50)`
Move to a defined position.

- **Parameters**:
  - `sts_id` (int)
  - `position` (int)
  - `speed` (int)
  - `acc` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.MoveTo(1, 2048)
```

---

### `WritePosition(sts_id, position)`
Direct position write.

- **Parameters**:
  - `sts_id` (int)
  - `position` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.WritePosition(1, 2048)
```

---

### `ReadPosition(sts_id)`
Read current position.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
servo.ReadPosition(1)
```

---

### `ReadSpeed(sts_id)`
Get current speed.

- **Parameters**: `sts_id` (int)
- **Returns**: `(int, int, int)`
- **Example**:
```python
speed, comm, error = servo.ReadSpeed(1)
```

---

### `LockEprom(sts_id)`
Lock the EEPROM.

- **Parameters**: `sts_id` (int)
- **Returns**: `int`
- **Example**:
```python
servo.LockEprom(1)
```

---

### `UnLockEprom(sts_id)`
Unlock the EEPROM.

- **Parameters**: `sts_id` (int)
- **Returns**: `int`
- **Example**:
```python
servo.UnLockEprom(1)
```

---

### `ChangeId(sts_id, new_id)`
Change the servo ID.

- **Parameters**:
  - `sts_id` (int)
  - `new_id` (int)
- **Returns**: `None` or `str`
- **Example**:
```python
servo.ChangeId(1, 2)
```

---

### `DefineMiddle(sts_id)`
Define current position as center (2048).

- **Parameters**: `sts_id` (int)
- **Returns**: `True` or `None`
- **Example**:
```python
servo.DefineMiddle(1)
```

---

### `TareServo(sts_id)`
Calibrate min/max and redefine middle.

- **Parameters**: `sts_id` (int)
- **Returns**: `(min_position, max_position)` or `None`
- **Example**:
```python
min_pos, max_pos = servo.TareServo(1)
```

---

### `getBlockPosition(sts_id)`
Move to physical limit and return position.

- **Parameters**: `sts_id` (int)
- **Returns**: `int` or `None`
- **Example**:
```python
position = servo.getBlockPosition(1)
```

---



## ST3215 registers

| Memory First Address   | Function                                       |   Number of Bytes |   Initial Value | Storage Area   | Permission   | Minimum Value   | Maximum Value   | Unit         | Value Parsing                                                                                                                                                                                                                                                                                                                                                                                   |
|:-----------------------|:-----------------------------------------------|------------------:|----------------:|:---------------|:-------------|:----------------|:----------------|:-------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                      | Firmware major version number                  |               nan |             nan | EPROM          | read only    | nan             | nan             | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 1                      | Firmware minor version number                  |               nan |             nan | EPROM          | read only    | nan             | nan             | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 3                      | Servo major version number                     |               nan |             nan | EPROM          | read only    | nan             | nan             | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 4                      | Servo minor version number                     |               nan |             nan | EPROM          | read only    | nan             | nan             | nan          | nan                                                                                                                                                                                                                                                                                                                                                                                             |
| 0x5                    | ID                                             |               nan |             nan | EPROM          | read/write   | nan             | nan             | Baud         | A unique identification code on the bus, with no duplicate ID numbers allowed on the same bus. ID number 254 (0xFE) is the broadcast ID, and broadcasts do not receive response packets.                                                                                                                                                                                                        |
| 0x6                    | Baudrate                                       |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | 0-7 respectively represent baud rates as follows:                                                                                                                                                                                                                                                                                                                                               |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400                                                                                                                                                                                                                                                                                                                                    |
| 0x7                    | Return delay                                   |               nan |             nan | EPROM          | read/write   | nan             | nan             | 2us          | The minimum unit is 2us, and the maximum allowable setting for response delay is 254*2=508us                                                                                                                                                                                                                                                                                                    |
| 0x8                    | Response status level                          |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | 0: Except for read and PING instructions, other instructions do not return response packets.                                                                                                                                                                                                                                                                                                    |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1: Return response packets for all instructions                                                                                                                                                                                                                                                                                                                                                 |
| 0x9                    | Minimum angle                                  |               nan |             nan | EPROM          | read/write   | nan             | --              | Step         | Set the minimum value limit for the motion range, which should be smaller than the maximum angle limit. When performing multi-turn absolute position control, this value is set to 0.                                                                                                                                                                                                           |
| 0xB                    | Maximum angle                                  |               nan |             nan | EPROM          | read/write   | --              | nan             | Step         | Set the maximum value limit for the motion range, which should be greater than the minimum angle limit. When performing multi-turn absolute position control, this value is set to 0.                                                                                                                                                                                                           |
| 0xD                    | Maximum temperature                            |               nan |             nan | EPROM          | read/write   | nan             | nan             | °C           | The maximum operating temperature limit, when set to 70, means the maximum temperature is 70 degrees Celsius, with a precision setting of 1 degree Celsius.                                                                                                                                                                                                                                     |
| 0xE                    | Maximum input voltage                          |               nan |             nan | EPROM          | read/write   | nan             | nan             | 0.1V         | If the maximum input voltage is set to 80, then the maximum operating voltage limit is 8.0V, with a precision setting of 0.1V.                                                                                                                                                                                                                                                                  |
| 0xF                    | Minimum input voltage                          |               nan |             nan | EPROM          | read/write   | nan             | nan             | 0.1V         | If the minimum input voltage is set to 40, then the minimum operating voltage limit is 4.0V, with a precision setting of 0.1V.                                                                                                                                                                                                                                                                  |
| 0x10                   | Maximum torque                                 |               nan |             nan | EPROM          | read/write   | nan             | nan             | nan          | Set the maximum output torque limit for the servo motor, where 1000 corresponds to 100% of the locked-rotor torque. Assign this value to address 48 upon power-up as the torque limit.                                                                                                                                                                                                          |
| 0x12                   | Phase                                          |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Special function byte, do not modify unless there are specific requirements. Please refer to the special byte bit analysis for further details.                                                                                                                                                                                                                                                 |
| 0x13                   | Unloading conditions                           |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 set corresponding bit to 1 to enable the corresponding protection.                                                                                                                                                                                                                                                                                              |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload set corresponding bit to 0 to disable the corresponding protection                                                                                                                                                                                                                                                                            |
| 0x14                   | LED alarm conditions                           |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 set the corresponding bit to 1 to enable flashing  LED.                                                                                                                                                                                                                                                                                                         |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload set corresponding bit to 0 to disable the corresponding protection                                                                                                                                                                                                                                                                            |
| 0x15                   | Position loop P (Proportional) coefficient     |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Proportional coefficient of control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x16                   | Position loop D (Differential) coefficient     |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Differential coefficient of control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x17                   | Position loop I (Integral) coefficient         |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Integral coefficient of the control motor                                                                                                                                                                                                                                                                                                                                                       |
| 0x18                   | Minimum starting force                         |               nan |             nan | EPROM          | read/write   | nan             | nan             | nan          | Set the minimum output startup torque for the servo, where 1000 corresponds to 100% of the locked-rotor torque.                                                                                                                                                                                                                                                                                 |
| 0x1A                   | Clockwise insensitive zone                     |               nan |             nan | EPROM          | read/write   | nan             | nan             | Step         | The minimum unit is one minimum resolution angle.                                                                                                                                                                                                                                                                                                                                               |
| 0x1B                   | Anti-clockwise insensitive zone                |               nan |             nan | EPROM          | read/write   | nan             | nan             | Step         | The minimum unit is a minimum resolution angle.                                                                                                                                                                                                                                                                                                                                                 |
| 0x1C                   | Protection current                             |               nan |             nan | EPROM          | read/write   | nan             | nan             | 6.5mA        | The maximum settable current is 500 * 6.5mA= 3250mA.                                                                                                                                                                                                                                                                                                                                            |
| 0x1E                   | Angle resolution                               |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | For the amplification factor of the minimum resolution angle (degree/step) of the sensor, modifying this value can expand the number of control range. When performing the multi-turn control, you need to modify the parameter at address 0x12 by setting BIT4 to 1. This modification will result in the current position feedback value being adjusted to reflect the larger angle feedback. |
| 0x1F                   | Position correction                            |               nan |             nan | EPROM          | read/write   | nan             | nan             | Step         | BIT11 is the direction bit, indicating the positive and negative direction, and other bits can indicate the range of 0-2047 steps.                                                                                                                                                                                                                                                              |
| 0x21                   | Operation mode                                 |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | 0: position servo mode                                                                                                                                                                                                                                                                                                                                                                          |
|                        |                                                |                   |                 |                |              |                 |                 |              | 1: motor constant speed mode, controlled by parameter 0x2E running speed parameter, the highest bit BIT15 is direction bit.                                                                                                                                                                                                                                                                     |
|                        |                                                |                   |                 |                |              |                 |                 |              | 2: PWM open-loop speed regulation mode, controlled by parameter 0x2Cthe  running time parameter, BIT10 is direction bit                                                                                                                                                                                                                                                                         |
|                        |                                                |                   |                 |                |              |                 |                 |              | 3: step servo mode, and the target position of parameter 0x2A is used to indicate the number of steps, and the highest bit BIT15 is the direction bit. When working                                                                                                                                                                                                                             |
|                        |                                                |                   |                 |                |              |                 |                 |              | In mode 3, the minimum and maximum angle limits of 0x9 and 0xB must be set to 0. Otherwise, it is impossible to step indefinitely.                                                                                                                                                                                                                                                              |
| 0x22                   | Protection torque                              |               nan |             nan | EPROM          | read/write   | nan             | nan             | nan          | Output torque after entering overload protection. If 20 is set, it means 20% of the maximum torque.                                                                                                                                                                                                                                                                                             |
| 0x23                   | Protection time                                |               nan |             nan | EPROM          | read/write   | nan             | nan             | 10ms         | The duration for which the current load output exceeds the overload torque and remains is represented by a value, such as 200, which indicates 2 seconds. The maximum value that can be set is 2.5 seconds.                                                                                                                                                                                     |
| 0x24                   | Overload torque                                |               nan |             nan | EPROM          | read/write   | nan             | nan             | nan          | The maximum torque threshold for starting the overload protection time countdown can be represented by a value, such as 80, indicating 80% of the maximum torque.                                                                                                                                                                                                                               |
| 0x25                   | Speed closed-loop proportional (P) coefficient |               nan |             nan | EPROM          | read/write   | nan             | nan             | None         | Proportional coefficient of speed loop in motor constant speed mode (mode 1)                                                                                                                                                                                                                                                                                                                    |
| 0x26                   | Overcurrent protection time                    |               nan |             nan | EPROM          | read/write   | nan             | nan             | 10ms         | The maximum setting is 254 * 10ms = 2540ms.                                                                                                                                                                                                                                                                                                                                                     |
| 0x27                   | Velocity closed-loop integral (I) coefficient  |               nan |             nan | EPROM          | read/write   | nan             | nan             | 1/10         | In the motor constant speed mode (mode 1), the speed loop integral coefficient (change note: the speed closed loop I integral coefficient is reduced by 10 times compared with version 3.6).                                                                                                                                                                                                    |
| 0x28                   | Torque switch                                  |               nan |             nan | SRAM           | read/write   | nan             | nan             | None         | Write 0: disable the torque output; Write 1: enable the torque output; Write 128: Arbitrary current position correction to 2048.                                                                                                                                                                                                                                                                |
| 0x29                   | Acceleration                                   |               nan |             nan | SRAM           | read/write   | nan             | nan             | 100 step/s^2 | If set to 10, it corresponds to an acceleration and deceleration rate of 1000 steps per second squared.                                                                                                                                                                                                                                                                                         |
| 0x2A                   | Target location                                |               nan |             nan | SRAM           | read/write   | nan             | nan             | Step         | Each step corresponds to the minimum resolution angle, and it is used in absolute position control mode. The maximum number of steps corresponds to the maximum effective angle.                                                                                                                                                                                                                |
| 0x2C                   | Operation time                                 |               nan |             nan | SRAM           | read/write   | nan             | nan             | nan          | In the PWM open-loop speed control mode, the value range is from 50 to 1000, and BIT10 serves as the direction bit.                                                                                                                                                                                                                                                                             |
| 0x2E                   | Operation speed                                |               nan |             nan | SRAM           | read/write   | nan             | nan             | step/s       | Number of steps per unit time (per second), 50 steps per second = 0.732 RPM (revolutions per minute)                                                                                                                                                                                                                                                                                            |
| 0x30                   | Torque limit                                   |               nan |             nan | SRAM           | read/write   | nan             | nan             | nan          | The initial value of power-on will be assigned by the maximum torque (0x10), which can be modified by the user to control the output of the maximum torque.                                                                                                                                                                                                                                     |
| 0x37                   | Lock flag                                      |               nan |             nan | SRAM           | read/write   | nan             | nan             | None         | Writing 0: Disables the write lock, allowing values written to the EPROM address to be saved even after power loss.                                                                                                                                                                                                                                                                             |
|                        |                                                |                   |                 |                |              |                 |                 |              | Writing 1: Enables the write lock, preventing values written to the EPROM address from being saved after power loss.                                                                                                                                                                                                                                                                            |
| 0x38                   | Current location                               |               nan |             nan | SRAM           | read only    | nan             | nan             | Step         | Feedback the number of steps in the current position, each step is a minimum resolution angle; Absolute position control mode, the maximum value corresponds to the maximum effective angle.                                                                                                                                                                                                    |
| 0x3A                   | Current speed                                  |               nan |             nan | SRAM           | read only    | nan             | nan             | step/s       | Feedback the current speed of motor rotation and the number of steps in unit time (per second).                                                                                                                                                                                                                                                                                                 |
| 0x3C                   | Current load                                   |               nan |             nan | SRAM           | read only    | nan             | nan             | nan          | The voltage duty cycle of the current control output driving motor.                                                                                                                                                                                                                                                                                                                             |
| 0x3E                   | Current voltage                                |               nan |             nan | SRAM           | read only    | nan             | nan             | 0.1V         | Current servo operation voltage                                                                                                                                                                                                                                                                                                                                                                 |
| 0x3F                   | Current temperature                            |               nan |             nan | SRAM           | read only    | nan             | nan             | °C           | Current servo internal operating temperature                                                                                                                                                                                                                                                                                                                                                    |
| 0x40                   | Asynchronous write flag                        |               nan |             nan | SRAM           | read only    | nan             | nan             | None         | The flag bit for using asynchronous write instructions                                                                                                                                                                                                                                                                                                                                          |
| 0x41                   | Servo status                                   |               nan |             nan | SRAM           | read only    | nan             | nan             | None         | Bit0  Bit1  Bit2 Bit3 Bit4 Bit5 the corresponding bit is set to 1 to indicate that the corresponding error occurs,                                                                                                                                                                                                                                                                              |
|                        |                                                |                   |                 |                |              |                 |                 |              | Voltage Sensor Temperature Current Angle Overload the corresponding bit is set to 0 to indicate that there is no corresponding error.                                                                                                                                                                                                                                                           |
| 0x42                   | Move flag                                      |               nan |             nan | SRAM           | read only    | nan             | nan             | None         | The sign of the servo is 1 when it is moving, and 0 when it is stopped.                                                                                                                                                                                                                                                                                                                         |
| 0x45                   | Current current                                |               nan |             nan | SRAM           | read only    | nan             | nan             | 6.5mA        | The maximum measurable current is 500 * 6.5mA= 3250mA.                                                                                                                                                                                                                                                                                                                                          |

## License

Apache 2 License

## Author

Mickael Roger (mickael@mickael-roger.com)

