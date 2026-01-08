# ST3215 Test Suite

This directory contains individual test scripts for testing ST3215 servo motor functionality. Each test focuses on specific functionality and can be run independently.

## Prerequisites

### Hardware Requirements
- ST3215 servo motor with ID 1 connected to the system
- USB-to-Serial adapter (RS-485 or TTL depending on your setup)
- Proper power supply for the servo motor

### Software Requirements
- Python 3.10+
- st3215 library installed (`pip install -e .` from project root)
- pyserial dependency

## Environment Setup

Set the USB device path in your environment:

```bash
export ST3215_DEV="/dev/ttyUSB0" 
```

## Running Tests

Each test can be executed individually:

```bash
python test_01_ping_servo.py
python test_02_list_servos.py
# ... etc
```

Or run all tests in sequence:

```bash
for test in test_*.py; do echo "Running $test"; python "$test"; echo; done
```

## Test Descriptions

### Test 01: PingServo
Tests basic communication with servo ID 1.
- **File**: `test_01_ping_servo.py`
- **Purpose**: Verify servo is connected and responding

### Test 02: ListServos
Scans the bus for all connected servos.
- **File**: `test_02_list_servos.py`
- **Purpose**: Discover all servos on the bus

### Test 03: Read Load, Voltage & Current
Tests telemetry reading functions.
- **File**: `test_03_read_load_voltage_current.py`
- **Purpose**: Read motor load, supply voltage, and current consumption
- **⚠️ Special Instructions**: Apply physical force to the servo motor shaft, then press Enter before running this test

### Test 04: ReadTemperature
Tests temperature sensor reading.
- **File**: `test_04_read_temperature.py`
- **Purpose**: Read internal servo temperature

### Test 05: ReadAcceleration
Tests acceleration parameter reading.
- **File**: `test_05_read_acceleration.py`
- **Purpose**: Read current acceleration setting

### Test 06: ReadMode
Tests operational mode reading.
- **File**: `test_06_read_mode.py`
- **Purpose**: Read current servo operation mode

### Test 07: ReadCorrection
Tests position correction reading.
- **File**: `test_07_read_correction.py`
- **Purpose**: Read position correction value

### Test 08: ReadStatus
Tests servo status reading.
- **File**: `test_08_read_status.py`
- **Purpose**: Read servo sensor status flags

### Test 09: IsMoving
Tests motion detection.
- **File**: `test_09_is_moving.py`
- **Purpose**: Check if servo is currently moving

### Test 10: Complete Motion Control
Comprehensive test of servo control functions.
- **File**: `test_10_complete_motion_control.py`
- **Purpose**: Test StartServo, SetAcceleration, SetSpeed, rotation mode, position mode, and StopServo
- **⚠️ Important**: Ensure servo has enough physical clearance for movement

### Test 11: Change baudrate
Tests baud rate changing functionality.
- **File**: `test_11_change_baudrate.py`
- **Purpose**: Change servo communication baud rate and verify

### Test 12: Read Position
Tests position reading functionality.
- **File**: `test_12_read_position.py`
- **Purpose**: Read current servo position

## Safety Notes

- Ensure proper power supply is connected before running tests
- Verify servo has adequate clearance for movement in Test 10
- Stop execution immediately if unusual noises or behaviors occur
- Test 03 requires manual interaction (applying force)

## Troubleshooting

### Common Issues

1. **Permission denied on /dev/ttyUSB0**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

2. **Servo not responding**:
   - Check power supply
   - Verify correct baud rate
   - Ensure proper wiring
   - Confirm servo ID is set to 1

3. **Import errors**:
   - Install library: `pip install -e .` from project root
   - Check Python path

## Expected Output

Each test will display:
- Test description
- Connection status
- Test results with actual values
- Success/failure indication

Example output:
```
=== ST3215 Ping Test ===
Device: /dev/ttyUSB0
Testing ping to servo ID 1...
✓ Servo ID 1 responded successfully
Test completed successfully!
```
