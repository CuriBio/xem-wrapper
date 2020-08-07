# -*- coding: utf-8 -*-
"""Everything goes here until we can reorganize the package."""

import os
import struct
from typing import cast
from typing import Optional

from .constants import BLOCK_SIZE
from .constants import DATA_FRAME_SIZE_WORDS
from .constants import DATA_FRAMES_PER_ROUND_ROBIN
from .constants import HEADER_MAGIC_NUMBER
from .constants import PIPE_OUT_FIFO
from .constants import TRIGGER_IN_SPI
from .constants import WIRE_IN_NUM_SAMPLES
from .constants import WIRE_IN_RESET_MODE
from .constants import WIRE_OUT_IS_PLL_LOCKED
from .constants import WIRE_OUT_IS_SPI_RUNNING
from .constants import WIRE_OUT_NUM_WORDS_FIFO
from .exceptions import OpalKellyFileNotFoundError
from .exceptions import OpalKellyFrontPanelNotSupportedError
from .exceptions import OpalKellyHeaderNotEightBytesError
from .exceptions import OpalKellyIDGreaterThan32BytesError
from .exceptions import OpalKellyNoDeviceFoundError
from .exceptions import OpalKellySampleIdxNotFourBytesError
from .exceptions import OpalKellyWordNotTwoBytesError
from .exceptions import parse_hardware_return_code
from .ok import FrontPanelDevices
from .ok import okCFrontPanel
from .ok import okTDeviceInfo


def build_header_magic_number_bytes(header_magic_number: int) -> bytearray:
    """Generate bytes of header magic number.

    Args:
        header_magic_number: 8 bytes wide, little-endian

    Returns:
        Little endian bytearray of the header magic number.
    """
    header_magic_number_bytes = struct.pack(
        "<2L",
        (header_magic_number & 0xFFFFFFFF00000000) >> 32,
        header_magic_number & 0xFFFFFFFF,
    )
    return bytearray(header_magic_number_bytes)


def read_wire_out(xem: okCFrontPanel, ep_addr: int) -> int:
    """Get the most recent value from the wire-out endpoint.

    Args:
        xem: the XEM7310 on which to read the desired wire-out
        ep_addr: the address of the desired wire-out endpoint

    Return:
        The value of the desired wire-out.
    """
    parse_hardware_return_code(xem.UpdateWireOuts())
    result: int = (xem.GetWireOutValue(ep_addr))
    parse_hardware_return_code(result)
    return result


def set_wire_in(xem: okCFrontPanel, ep_addr: int, value: int, mask: int) -> None:
    """Set a value to the specified bits on the wire-in endpoint.

    Args:
        xem: the XEM7310 on which to set the desired wire-in value
        ep_addr: the address of the desired wire-in endpoint
        value: bitwise value to set on the wire
        mask: bit mask to apply to the given value
    """
    parse_hardware_return_code(xem.SetWireInValue(ep_addr, value, mask))
    parse_hardware_return_code(xem.UpdateWireIns())


def read_from_fifo(xem: okCFrontPanel) -> bytearray:
    """Read all unread data from the FIFO of the given XEM7310 board.

    Args:
        xem: the XEM7310 to read data from

    Return:
        A bytearray containing all data in the FIFO at the time of the read
    """
    num_words_fifo = get_num_words_fifo(xem)
    if num_words_fifo < DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN:
        return bytearray(0)

    incomplete_round_robin_words = num_words_fifo % (
        DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN
    )
    num_words_to_read = num_words_fifo - incomplete_round_robin_words
    data_buffer = bytearray(num_words_to_read * 4)
    # enable read mode
    set_wire_in(xem, WIRE_IN_RESET_MODE, 0x0002, 0x0002)
    read_result = xem.ReadFromBlockPipeOut(PIPE_OUT_FIFO, BLOCK_SIZE, data_buffer)
    parse_hardware_return_code(read_result)
    # disable read mode
    set_wire_in(xem, WIRE_IN_RESET_MODE, 0x0000, 0x0002)
    return data_buffer


def reset_fifos(xem: okCFrontPanel) -> None:
    """Reset the FIFOs.

    Args:
        xem: the XEM7310 to reset the fifos of
    """
    # set reset bit high
    set_wire_in(xem, 0x00, 0x0004, 0x0004)
    # clear reset bit
    set_wire_in(xem, 0x00, 0x0000, 0x0004)


def convert_sample_idx(sample_idx_bytes: bytearray) -> int:
    """Convert sample index from board to numeric integer.

    Args:
        sample_idx_bytes: 4 bytes wide, little-endian

    Return:
        Integer representation of the time index of the sample.
    """
    if len(sample_idx_bytes) != 4:
        raise OpalKellySampleIdxNotFourBytesError()
    sample_idx = struct.unpack("<I", sample_idx_bytes)[0]
    if not isinstance(sample_idx, int):
        raise NotImplementedError("sample_idx should always be an integer value.")
    return sample_idx


def convert_word(word_bytes: bytearray) -> int:
    """Convert word from board to numeric integer.

    Args:
        word_bytes: 2 bytes wide, little-endian

    Return:
        Integer representation of the word.
    """
    if len(word_bytes) != 2:
        raise OpalKellyWordNotTwoBytesError()
    return word_bytes[0] + (word_bytes[1] << 8)


def convert_wire_value(value: int) -> int:
    """Convert endianness of given 32-bit value.

    Big Endian values become Little Endian and Little Endian values become Big Endian.

    Specifically for use when reading wire_out values from OK device or simulator
    """
    converted_value: int = struct.unpack("<I", struct.pack(">I", value))[0]
    return converted_value


def check_header(header_bytes: bytearray) -> bool:
    """Check that the received header magics the magic number.

    Args:
        header_bytes: 8 bytes wide, little-endian

    Return:
        True if header matches, False otherwise
    """
    if len(header_bytes) != 8:
        raise OpalKellyHeaderNotEightBytesError()
    header_words = struct.unpack("<2L", header_bytes)
    if not isinstance(header_words[0], int) or not isinstance(header_words[1], int):
        raise NotImplementedError("header_words should always be integer values.")
    header = (header_words[0] << 32) + header_words[1]
    return header == HEADER_MAGIC_NUMBER


def start_acquisition(xem: okCFrontPanel) -> None:
    """Begin running SPI data acquisition on the FPGA of the XEM7310.

    Args:
        xem: XEM7310 board to start running SPI data acquisition on
    """
    activate_trigger_in(xem, TRIGGER_IN_SPI, 0)


def stop_acquisition(xem: okCFrontPanel) -> None:
    """Stop running SPI data acquisition on the FPGA of the XEM7310.

    Args:
        xem: XEM7310 board to stop running SPI data acquisition on
    """
    activate_trigger_in(xem, TRIGGER_IN_SPI, 1)


def is_spi_running(xem: okCFrontPanel) -> bool:
    """Check to see if SPI data acquisition on the given XEM7310 is running.

    Args:
        xem: XEM7310 board to check SPI data acquisition status of

    Return:
        True if SPI data acquisition is running, False otherwise
    """
    result = read_wire_out(xem, WIRE_OUT_IS_SPI_RUNNING)
    return result & 0x00000001 == 0x00000001


def is_pll_locked(xem: okCFrontPanel) -> bool:
    """Check to see if the pll on the given XEM6310 is locked.

    Args:
        xem: XEM7310 board to check the pll on

    Return:
        True if the pll is locked, False otherwise
    """
    pll_status = read_wire_out(xem, WIRE_OUT_IS_PLL_LOCKED)
    return pll_status & 0x00000001 == 0x00000001


def set_run_mode(xem: okCFrontPanel, continuous: bool) -> None:
    """Set the XEM7310 board to run SPI data acquisition continuously or not.

    Args:
        xem: XEM7310 board to set value on
        continuous: whether to have the XEM7310 run SPI data acquisition
                    continuously or not
    """
    value = 0x00000002 if continuous else 0x00000000
    set_wire_in(xem, WIRE_IN_RESET_MODE, value, 0x00000002)


def open_board() -> okCFrontPanel:
    """Open a communication line to an Opal Kelly board if one is connected.

    Return:
        xem: okCFrontPanel object used to control the XEM7310
    """
    devices = FrontPanelDevices()  # type: ignore
    xem = cast(okCFrontPanel, devices.Open())
    if not xem:
        raise OpalKellyNoDeviceFoundError()
    return xem


def initialize_board(xem: okCFrontPanel, bit_file_name: Optional[str] = None) -> None:
    """Initialize the FPGA of the given XEM7310 using the specified bit file.

    Args:
        xem: XEM7310 board to initialize the FPGA of
        bit_file_name: name of the '.bit' file to upload to the XEM7310 board
    """
    if bit_file_name is not None:
        check_file_exists(bit_file_name)
        hardware_return_code = xem.ConfigureFPGA(bit_file_name)
        parse_hardware_return_code(hardware_return_code)
    if not xem.IsFrontPanelEnabled():
        raise OpalKellyFrontPanelNotSupportedError()


def check_file_exists(file_path: str) -> None:
    """Raise error if file path is not found."""
    if not os.path.isfile(file_path):
        raise OpalKellyFileNotFoundError(
            f"Path: {file_path} not found from Current Working Directory: {os.getcwd()}"
        )


def _get_device_info(xem: okCFrontPanel) -> okTDeviceInfo:
    info = cast(okTDeviceInfo, okTDeviceInfo())  # type: ignore

    hardware_return_code = xem.GetDeviceInfo(info)
    parse_hardware_return_code(hardware_return_code)
    return info


def get_serial_number(xem: okCFrontPanel) -> str:
    """Get the serial number of the given XEM7310 board.

    Args:
        xem: XEM7310 board to get the serial number of

    Return:
        The serial number of the given XEM7310
    """
    serial_number = _get_device_info(xem).serialNumber
    if not isinstance(serial_number, str):
        raise NotImplementedError(
            "The okTDeviceInfo is always supposed to have a string as the serial number attribute."
        )

    return serial_number


def get_num_words_fifo(xem: okCFrontPanel) -> int:
    """Get the number of 4 byte words in the FIFO of the given XEM7310 board.

    Args:
        xem: XEM7310 board to check the FIFO of

    Return:
        The number of words in the FIFO
    """
    return read_wire_out(xem, WIRE_OUT_NUM_WORDS_FIFO)


def get_device_id(xem: okCFrontPanel) -> str:
    """Get the ID of the given XEM7310 board.

    Args:
        xem: XEM7310 board to get the ID of

    Return:
        The ID string of the XEM7310
    """
    device_id = _get_device_info(xem).deviceID
    if not isinstance(device_id, str):
        raise NotImplementedError(
            "The okTDeviceInfo is always supposed to have a string as the deviceID attribute."
        )
    return device_id


def set_device_id(xem: okCFrontPanel, new_id: str) -> None:
    """Set the ID of the given XEM7310 board.

    Args:
        xem: XEM7310 board to set the new ID of
        new_id: the desired ID string to set. Can be 0-32 bytes long and
                can contain unicode characters.
    """
    validate_device_id(new_id)
    hardware_return_code = xem.SetDeviceID(new_id)
    parse_hardware_return_code(hardware_return_code)


def validate_device_id(new_id: str) -> None:
    """Validate the new ID.

    Args:
        new_id: ID string to validate
    """
    if len(new_id.encode("utf-8")) > 32:
        raise OpalKellyIDGreaterThan32BytesError()


def set_num_samples(xem: okCFrontPanel, num_samples: int) -> None:
    """Set the number of samples for SPI data acquisition to take on the FPGA.

    Args:
        xem: XEM7310 board to set value on
        num_samples: desired number of samples to take
    """
    set_wire_in(xem, WIRE_IN_NUM_SAMPLES, num_samples, 0xFFFFFFFF)


def activate_trigger_in(xem: okCFrontPanel, ep_addr: int, bit: int) -> None:
    """Activate the specified bit of the given trigger in on the XEM7310.

    Args:
        xem: XEM7310 board to activate trigger in on
        ep_addr: address of given trigger in endpoint
        bit: bit of the trigger in to set. Should only be one nonzero bit
    """
    hardware_return_code = xem.ActivateTriggerIn(ep_addr, bit)
    parse_hardware_return_code(hardware_return_code)
