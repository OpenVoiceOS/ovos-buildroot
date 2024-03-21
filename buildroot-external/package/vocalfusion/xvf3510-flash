#!/usr/bin/env python3
# Copyright (c) 2019-2020, XMOS Ltd, All rights reserved
# requires dtparam=spi=on in /boot/config.txt

"""
This script configures the XVF3510 board to boot from SPI slave and loads a
binary file. It requires a bin file as an input parameter.
"""

import sys
import time
import argparse
from smbus2 import SMBus
import digitalio
import busio
from pathlib import Path
import board
from typing import Optional

# Global variables for GPIO pins
BOOT_SEL_PIN = digitalio.DigitalInOut(board.D26)  # GPIO pin used for boot selection (PIN 37)
RST_N_PIN = digitalio.DigitalInOut(board.D27)     # GPIO pin used for reset (PIN 13)
I2C_ADDRESS = 0x2C                                # I2C address for the I/O expander. TODO: 0x20 was in original code, misstake?

if sys.version_info[0] < 3:
    print("This script requires Python 3.")
    sys.exit(1)

def bit_reversed_byte(byte_to_reverse: int) -> int:
    """
    Reverse the bits of a byte.

    Args:
        byte_to_reverse (int): The byte to reverse.

    Returns:
        int: The reversed byte.
    """
    return int("{:08b}".format(byte_to_reverse)[::-1], 2)


def set_boot_sel() -> None:
    """
    Set XVF3510 board in SPI slave boot mode using I2C to manipulate BOOT_SEL pin.
    """
    try:
        with SMBus(1) as bus:
            # Reset BOOT_SEL to default
            bus.write_byte_data(I2C_ADDRESS, 3, 0xFE)
            bus.write_byte_data(I2C_ADDRESS, 7, 0xFF)

            # Preserve other settings while manipulating BOOT_SEL
            state = {i: bus.read_byte_data(I2C_ADDRESS, i) for i in [2, 6]}

            # Start reset sequence
            for i in [2, 6]:
                bus.write_byte_data(I2C_ADDRESS, i, 0x00 | (state[i] & 0xDF))
            # Set BOOT_SEL high
            bus.write_byte_data(I2C_ADDRESS, 3, 0x01)
            bus.write_byte_data(I2C_ADDRESS, 7, 0xFE)
            # End reset sequence
            for i in [2, 6]:
                bus.write_byte_data(I2C_ADDRESS, i, 0x20 | (state[i] & 0xDF))
    except Exception as e:
        print(f"Error setting BOOT_SEL via I2C: {e}")
        sys.exit(1)


def send_image(
    bin_filename: str,
    verbose: bool = False,
    max_spi_speed_mhz: float = 5,
    block_transfer_pause_ms: float = 1,
    direct: bool = False,
    delay: bool = False,
) -> None:
    """
    Send the given image to the device via SPI slave.

    Args:
        bin_filename (str): Binary file name.
        verbose (bool, optional): Enable verbose output. Defaults to False.
        max_spi_speed_mhz (float, optional): Max SPI speed in MHz. Defaults to 5.
        block_transfer_pause_ms (float, optional): Pause between blocks in milliseconds. Defaults to 1.
        direct (bool, optional): Direct mode flag. Defaults to False.
        delay (bool, optional): Delay startup flag. Defaults to False.
    """
    binary_size = Path(bin_filename).stat().st_size
    print(f'Read file "{bin_filename}" size: {binary_size} Bytes')

    if direct:
        BOOT_SEL_PIN.switch_to_input()
        RST_N_PIN.switch_to_output()
        RST_N_PIN.value=1

    spi = setup_spi(max_spi_speed_mhz)

    if direct:
        RST_N_PIN.value=False
        BOOT_SEL_PIN.switch_to_output()
        BOOT_SEL_PIN.value=True
        RST_N_PIN.value=True
    else:
        set_boot_sel()

    reverse_table = [bit_reversed_byte(byte) for byte in range(256)]

    try:
        with open(bin_filename, "rb") as f:
            data = list(f.read())
    except Exception as e:
        print(f"Error reading binary file: {e}")
        sys.exit(1)

    send_data_over_spi(data, spi, reverse_table, verbose, block_transfer_pause_ms, direct, delay)

    print("Sending complete")

    if direct:
        # Once booted, the Pi should not need to drive boot_sel and reset
        BOOT_SEL_PIN.switch_to_input()
        RST_N_PIN.value=True
    else:
        # Reset BOOT_SEL to default state
        with SMBus(1) as bus:
            bus.write_byte_data(I2C_ADDRESS, 3, 0xFE)
            bus.write_byte_data(I2C_ADDRESS, 7, 0xFF)


def setup_spi(max_spi_speed_mhz: float) -> busio.SPI:
    """
    Set up the SPI bus.

    Args:
        max_spi_speed_mhz (float): Max SPI speed in MHz.

    Returns:
        busio.SPI: Configured SPI bus.
    """
    spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)
    while not spi.try_lock():
        pass
    spi.configure(baudrate=max_spi_speed_mhz * 1_000_000)
    return spi


def send_data_over_spi(
    data: list,
    spi: busio.SPI,
    reverse_table: list,
    verbose: bool,
    pause_ms: float,
    direct: bool,
    delay: bool,
) -> None:
    """
    Send data over SPI, handling block transfers and optional delays.

    Args:
        data (list): Data to send.
        spi (busio.SPI): Configured SPI bus.
        reverse_table (list): Table of bit-reversed byte values.
        verbose (bool): Enable verbose output.
        pause_ms (float): Pause between blocks in milliseconds.
        direct (bool): Direct mode flag.
        delay (bool): Delay startup flag.
    """
    spi_block_size = 4096
    block_count = 0
    total_data_length = len(data)
    for i in range(0, total_data_length, spi_block_size):
        block = [reverse_table[byte] for byte in data[i : i + spi_block_size]]
        if verbose:
            print(f"Sending {len(block)} Bytes in block {block_count} checksum 0x{sum(block):X}")
        spi.write(block)

        # Update the remaining data length after each block transfer
        remaining_data_length = total_data_length - (i + len(block))
        handle_block_transfer(
            block_count, delay, direct, pause_ms, remaining_data_length
        )
        block_count += 1


def handle_block_transfer(
    block_count: int, delay: bool, direct: bool, pause_ms: float, remaining_data_length: int
) -> None:
    """
    Handle specifics of block transfer, including initial delays and conditional logic for direct mode.

    Args:
        block_count (int): Number of blocks sent.
        delay (bool): Delay startup flag.
        direct (bool): Direct mode flag.
        pause_ms (float): Pause between blocks in milliseconds.
        remaining_data_length (int): Length of remaining data to send.
    """
    if block_count == 0:
        # Long delay for PLL reboot
        time.sleep(0.1)

        if delay:
            # release boot_sel early to prevent startup
            if direct:
                # release boot_sel early to prevent startup
                BOOT_SEL_PIN.switch_to_input()
            else:
                # Reset BOOT_SEL to default state
                with SMBus(1) as bus:
                    bus.write_byte_data(I2C_ADDRESS, 3, 0xFE)
                    bus.write_byte_data(I2C_ADDRESS, 7, 0xFF)

    elif remaining_data_length > 0:
        time.sleep(pause_ms / 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load an image via SPI slave from an RPi")
    parser.add_argument("bin_filename", help="binary file name")
    parser.add_argument("--direct", action="store_true", help="Use direct GPIO outputs rather than the XVF3510 Development Kit Pi HAT")
    parser.add_argument("--delay", action="store_true", help="Delay xvf3510 device start")
    parser.add_argument("--max-spi-speed-mhz", type=float, default=5, help="Max SPI speed in MHz")
    parser.add_argument("--block-transfer-pause-ms", type=float, default=1, help="Pause between SPI transfers in milliseconds")
    parser.add_argument("--verbose", action="store_true", help="Print debug information")
    args = parser.parse_args()

    bin_path = Path(args.bin_filename)
    if not bin_path.is_file():
        print(f"Error: input file {bin_path} not found")
        sys.exit(1)

    start_time = time.time()
    send_image(
        bin_path,
        args.verbose,
        args.max_spi_speed_mhz,
        args.block_transfer_pause_ms,
        args.direct,
        args.delay,
    )
    end_time = time.time()

    BOOT_SEL_PIN.deinit()
    RST_N_PIN.deinit()

    if args.verbose:
        print(f"Sending image took {end_time - start_time:.3f} seconds")

