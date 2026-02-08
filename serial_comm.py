"""
Serial Communication Module

This module provides functionality to open a COM port, read data, and close the port.
Designed for use with NI TestStand with separate initialize, read, and close functions.
"""

import serial
from typing import Optional, Tuple, Dict, List

# Store open serial connections
_connections: Dict[str, serial.Serial] = {}


def initialize_port(
    port: str,
    baudrate: int = 9600,
    timeout: Optional[float] = None,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: float = 1
) -> Tuple[bool, str]:
    """
    Initialize and open a COM port.

    Args:
        port: The COM port to open (e.g., 'COM1', 'COM3').
        baudrate: The baud rate for serial communication. Defaults to 9600.
        timeout: Read timeout in seconds. None means wait indefinitely.
        bytesize: Number of data bits (5, 6, 7, 8). Defaults to 8.
        parity: Parity checking ('N'=None, 'E'=Even, 'O'=Odd, 'M'=Mark, 'S'=Space). Defaults to 'N'.
        stopbits: Number of stop bits (1, 1.5, 2). Defaults to 1.

    Returns:
        Tuple containing:
            - success (bool): True if port opened successfully, False otherwise.
            - message (str): Status message or error description.
    """
    # Map parity string to serial constants
    parity_map = {
        "N": serial.PARITY_NONE,
        "E": serial.PARITY_EVEN,
        "O": serial.PARITY_ODD,
        "M": serial.PARITY_MARK,
        "S": serial.PARITY_SPACE
    }

    # Map bytesize to serial constants
    bytesize_map = {
        5: serial.FIVEBITS,
        6: serial.SIXBITS,
        7: serial.SEVENBITS,
        8: serial.EIGHTBITS
    }

    # Map stopbits to serial constants
    stopbits_map = {
        1: serial.STOPBITS_ONE,
        1.5: serial.STOPBITS_ONE_POINT_FIVE,
        2: serial.STOPBITS_TWO
    }

    # Check if port is already open
    if port in _connections and _connections[port].is_open:
        return (False, f"Port {port} is already open")

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize_map.get(bytesize, serial.EIGHTBITS),
            parity=parity_map.get(parity.upper(), serial.PARITY_NONE),
            stopbits=stopbits_map.get(stopbits, serial.STOPBITS_ONE),
            timeout=timeout
        )
        _connections[port] = ser
        return (True, f"Port {port} opened at {baudrate} baud")

    except serial.SerialException as e:
        return (False, f"Serial error: {e}")
    except Exception as e:
        return (False, f"Error: {e}")


def send_data(port: str, message: str, encoding: str = "utf-8") -> Tuple[bool, str]:
    """
    Send a string message through an open COM port.

    Args:
        port: The COM port to send data through (e.g., 'COM1', 'COM3').
        message: The string message to send.
        encoding: Character encoding for converting string to bytes. Defaults to 'utf-8'.

    Returns:
        Tuple containing:
            - success (bool): True if data was sent successfully, False otherwise.
            - message (str): Status message or error description.
    """
    if port not in _connections or not _connections[port].is_open:
        return (False, f"Port {port} is not open")

    try:
        ser = _connections[port]
        data_bytes = message.encode(encoding)
        bytes_written = ser.write(data_bytes)
        return (True, f"Sent {bytes_written} bytes")

    except serial.SerialException as e:
        return (False, f"Serial error: {e}")
    except Exception as e:
        return (False, f"Error: {e}")


def send_and_receive(port: str, message: str, encoding: str = "utf-8") -> Tuple[bool, str, str]:
    """
    Send a string message and wait for a response.

    Args:
        port: The COM port to use (e.g., 'COM1', 'COM3').
        message: The string message to send.
        encoding: Character encoding for string conversion. Defaults to 'utf-8'.

    Returns:
        Tuple containing:
            - success (bool): True if send and receive were successful, False otherwise.
            - message (str): Status message or error description.
            - response (str): The response received as a string (empty if failed).
    """
    success, status = send_data(port, message, encoding)
    if not success:
        return (False, status, "")

    success, status, response = read_data_as_string(port, encoding)
    return (success, status, response)


def send_and_receive_hex(port: str, message: str, encoding: str = "utf-8") -> Tuple[bool, str, List[int]]:
    """
    Send a string message and wait for a response as hex array.

    Args:
        port: The COM port to use (e.g., 'COM1', 'COM3').
        message: The string message to send.
        encoding: Character encoding for sending string. Defaults to 'utf-8'.

    Returns:
        Tuple containing:
            - success (bool): True if send and receive were successful, False otherwise.
            - message (str): Status message or error description.
            - response (List[int]): The response as a list of integer values (0-255).
    """
    success, status = send_data(port, message, encoding)
    if not success:
        return (False, status, [])

    success, status, response = read_data_as_hex(port)
    return (success, status, response)


def read_data(port: str) -> Tuple[bool, str, bytes]:
    """
    Read data from an open COM port. Waits until data is available.

    Args:
        port: The COM port to read from (e.g., 'COM1', 'COM3').

    Returns:
        Tuple containing:
            - success (bool): True if data was received successfully, False otherwise.
            - message (str): Status message or error description.
            - data (bytes): The data received from the serial port (empty if failed).
    """
    if port not in _connections or not _connections[port].is_open:
        return (False, f"Port {port} is not open", b"")

    try:
        ser = _connections[port]

        # Wait until at least one byte is available
        while ser.in_waiting == 0:
            if ser.timeout is not None:
                break

        if ser.in_waiting == 0:
            return (False, "Timeout: No data received", b"")

        # Read all available data
        data = ser.read(ser.in_waiting)
        return (True, f"Received {len(data)} bytes", data)

    except serial.SerialException as e:
        return (False, f"Serial error: {e}", b"")
    except Exception as e:
        return (False, f"Error: {e}", b"")


def read_data_as_string(port: str, encoding: str = "utf-8") -> Tuple[bool, str, str]:
    """
    Read data from an open COM port and return as a string.

    Args:
        port: The COM port to read from (e.g., 'COM1', 'COM3').
        encoding: Character encoding for decoding bytes to string. Defaults to 'utf-8'.

    Returns:
        Tuple containing:
            - success (bool): True if data was received successfully, False otherwise.
            - message (str): Status message or error description.
            - data (str): The data received as a decoded string (empty if failed).
    """
    success, message, data_bytes = read_data(port)

    if success:
        try:
            data_str = data_bytes.decode(encoding, errors="replace")
            return (True, message, data_str)
        except Exception as e:
            return (False, f"Decode error: {e}", "")

    return (False, message, "")


def read_data_as_hex(port: str) -> Tuple[bool, str, List[int]]:
    """
    Read data from an open COM port and return as a list of hex values (integers).

    Args:
        port: The COM port to read from (e.g., 'COM1', 'COM3').

    Returns:
        Tuple containing:
            - success (bool): True if data was received successfully, False otherwise.
            - message (str): Status message or error description.
            - data (List[int]): The data as a list of integer values (0-255).

    Example:
        Returns: (True, "Received 3 bytes", [0x1A, 0x2B, 0x3C])
        Which is equivalent to: (True, "Received 3 bytes", [26, 43, 60])
    """
    success, message, data_bytes = read_data(port)

    if success:
        hex_array = list(data_bytes)
        return (True, message, hex_array)

    return (False, message, [])


def close_port(port: str) -> Tuple[bool, str]:
    """
    Close an open COM port.

    Args:
        port: The COM port to close (e.g., 'COM1', 'COM3').

    Returns:
        Tuple containing:
            - success (bool): True if port closed successfully, False otherwise.
            - message (str): Status message or error description.
    """
    if port not in _connections:
        return (False, f"Port {port} was not initialized")

    try:
        ser = _connections[port]
        if ser.is_open:
            ser.close()
        del _connections[port]
        return (True, f"Port {port} closed")

    except serial.SerialException as e:
        return (False, f"Serial error: {e}")
    except Exception as e:
        return (False, f"Error: {e}")


def close_all_ports() -> Tuple[bool, str]:
    """
    Close all open COM ports.

    Returns:
        Tuple containing:
            - success (bool): True if all ports closed successfully, False otherwise.
            - message (str): Status message listing closed ports.
    """
    closed_ports = []
    errors = []

    for port in list(_connections.keys()):
        success, message = close_port(port)
        if success:
            closed_ports.append(port)
        else:
            errors.append(f"{port}: {message}")

    if errors:
        return (False, f"Errors closing ports: {'; '.join(errors)}")

    if closed_ports:
        return (True, f"Closed ports: {', '.join(closed_ports)}")

    return (True, "No ports to close")


def is_port_open(port: str) -> bool:
    """
    Check if a COM port is currently open.

    Args:
        port: The COM port to check (e.g., 'COM1', 'COM3').

    Returns:
        bool: True if the port is open, False otherwise.
    """
    return port in _connections and _connections[port].is_open
