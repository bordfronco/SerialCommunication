"""
Serial Communication Module

This module provides functionality to open a COM port, wait for incoming data,
and return the received data. Designed for use with NI TestStand.
"""

import argparse
import serial
from typing import Optional, Tuple


def receive_data(
    port: str,
    baudrate: int = 9600,
    timeout: Optional[float] = None,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: float = 1
) -> Tuple[bool, str, bytes]:
    """
    Open a COM port, wait for data to be received, and return the data.
    Designed to be called from NI TestStand.

    Args:
        port: The COM port to open (e.g., 'COM1', 'COM3').
        baudrate: The baud rate for serial communication. Defaults to 9600.
        timeout: Read timeout in seconds. None means wait indefinitely.
        bytesize: Number of data bits (5, 6, 7, 8). Defaults to 8.
        parity: Parity checking ('N'=None, 'E'=Even, 'O'=Odd, 'M'=Mark, 'S'=Space). Defaults to 'N'.
        stopbits: Number of stop bits (1, 1.5, 2). Defaults to 1.

    Returns:
        Tuple containing:
            - success (bool): True if data was received successfully, False otherwise.
            - message (str): Status message or error description.
            - data (bytes): The data received from the serial port (empty if failed).
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

    try:
        with serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize_map.get(bytesize, serial.EIGHTBITS),
            parity=parity_map.get(parity.upper(), serial.PARITY_NONE),
            stopbits=stopbits_map.get(stopbits, serial.STOPBITS_ONE),
            timeout=timeout
        ) as ser:
            # Wait until at least one byte is available
            while ser.in_waiting == 0:
                if timeout is not None:
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


def receive_data_as_string(
    port: str,
    baudrate: int = 9600,
    timeout: Optional[float] = None,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: float = 1,
    encoding: str = "utf-8"
) -> Tuple[bool, str, str]:
    """
    Open a COM port, wait for data to be received, and return the data as a string.
    Convenience function for NI TestStand when string data is expected.

    Args:
        port: The COM port to open (e.g., 'COM1', 'COM3').
        baudrate: The baud rate for serial communication. Defaults to 9600.
        timeout: Read timeout in seconds. None means wait indefinitely.
        bytesize: Number of data bits (5, 6, 7, 8). Defaults to 8.
        parity: Parity checking ('N'=None, 'E'=Even, 'O'=Odd, 'M'=Mark, 'S'=Space). Defaults to 'N'.
        stopbits: Number of stop bits (1, 1.5, 2). Defaults to 1.
        encoding: Character encoding for decoding bytes to string. Defaults to 'utf-8'.

    Returns:
        Tuple containing:
            - success (bool): True if data was received successfully, False otherwise.
            - message (str): Status message or error description.
            - data (str): The data received as a decoded string (empty if failed).
    """
    success, message, data_bytes = receive_data(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits
    )

    if success:
        try:
            data_str = data_bytes.decode(encoding, errors="replace")
            return (True, message, data_str)
        except Exception as e:
            return (False, f"Decode error: {e}", "")

    return (False, message, "")


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description="Serial communication - receive data from COM port")
    parser.add_argument("port", help="COM port (e.g., COM1, COM3)")
    parser.add_argument("-b", "--baudrate", type=int, default=9600, help="Baud rate (default: 9600)")
    parser.add_argument("-t", "--timeout", type=float, default=None, help="Read timeout in seconds (default: None)")
    parser.add_argument("--bytesize", type=int, choices=[5, 6, 7, 8], default=8, help="Data bits (default: 8)")
    parser.add_argument("--parity", choices=["N", "E", "O", "M", "S"], default="N", help="Parity: N=None, E=Even, O=Odd, M=Mark, S=Space (default: N)")
    parser.add_argument("--stopbits", type=float, choices=[1, 1.5, 2], default=1, help="Stop bits (default: 1)")

    args = parser.parse_args()

    success, message, data = receive_data(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        bytesize=args.bytesize,
        parity=args.parity,
        stopbits=args.stopbits
    )

    print(f"Success: {success}")
    print(f"Message: {message}")
    if success:
        print(f"Data (bytes): {data}")
        print(f"Data (string): {data.decode('utf-8', errors='replace')}")


if __name__ == "__main__":
    main()
