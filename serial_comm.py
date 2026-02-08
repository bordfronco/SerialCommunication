"""
Serial Communication Module

This module provides functionality to open a COM port, wait for incoming data,
and return the received data.
"""

import argparse
import serial
from typing import Optional


def receive_data(
    port: str,
    baudrate: int = 9600,
    timeout: Optional[float] = None,
    bytesize: int = serial.EIGHTBITS,
    parity: str = serial.PARITY_NONE,
    stopbits: float = serial.STOPBITS_ONE
) -> bytes:
    """
    Open a COM port, wait for data to be received, and return the data.

    Args:
        port: The COM port to open (e.g., 'COM1', 'COM3').
        baudrate: The baud rate for serial communication. Defaults to 9600.
        timeout: Read timeout in seconds. None means wait indefinitely.
        bytesize: Number of data bits. Defaults to 8.
        parity: Parity checking. Defaults to no parity.
        stopbits: Number of stop bits. Defaults to 1.

    Returns:
        bytes: The data received from the serial port.

    Raises:
        serial.SerialException: If the port cannot be opened or communication fails.
    """
    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        timeout=timeout
    ) as ser:
        print(f"Opened {port} at {baudrate} baud. Waiting for data...")

        # Wait until at least one byte is available
        while ser.in_waiting == 0:
            pass

        # Read all available data
        data = ser.read(ser.in_waiting)

        print(f"Received {len(data)} bytes")
        return data


def main():
    """Main entry point for the serial communication program."""
    parser = argparse.ArgumentParser(description="Serial communication - receive data from COM port")
    parser.add_argument("port", help="COM port (e.g., COM1, COM3)")
    parser.add_argument("-b", "--baudrate", type=int, default=9600, help="Baud rate (default: 9600)")
    parser.add_argument("-t", "--timeout", type=float, default=None, help="Read timeout in seconds (default: None)")
    parser.add_argument("--bytesize", type=int, choices=[5, 6, 7, 8], default=8, help="Data bits (default: 8)")
    parser.add_argument("--parity", choices=["N", "E", "O", "M", "S"], default="N", help="Parity: N=None, E=Even, O=Odd, M=Mark, S=Space (default: N)")
    parser.add_argument("--stopbits", type=float, choices=[1, 1.5, 2], default=1, help="Stop bits (default: 1)")

    args = parser.parse_args()

    # Map parity argument to serial constants
    parity_map = {
        "N": serial.PARITY_NONE,
        "E": serial.PARITY_EVEN,
        "O": serial.PARITY_ODD,
        "M": serial.PARITY_MARK,
        "S": serial.PARITY_SPACE
    }

    try:
        data = receive_data(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            bytesize=args.bytesize,
            parity=parity_map[args.parity],
            stopbits=args.stopbits
        )
        print(f"Data received: {data}")
        print(f"Data as string: {data.decode('utf-8', errors='replace')}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()
