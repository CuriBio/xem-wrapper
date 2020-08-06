# -*- coding: utf-8 -*-
"""Wraps the SWIG-generated API for the Opal Kelly FPGA Board.

FrontPanel 5.1.1 Files (ok.py, _ok.pyd, and _ok.so) can be downloaded by
registered customers only from Opal Kelly's Pin Downloads page:
https://pins.opalkelly.com/downloads

For all Opal Kelly boards, words are 32-bits wide.
"""
from . import front_panel
from . import main
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
from .exceptions import FPSimulatorInvalidFIFOValueError
from .exceptions import OkHardwareCommunicationError
from .exceptions import OkHardwareDataAlignmentError
from .exceptions import OkHardwareDeviceNotOpenError
from .exceptions import OkHardwareDoneNotHighError
from .exceptions import OkHardwareErrorNotRecognized
from .exceptions import OkHardwareFailedError
from .exceptions import OkHardwareFIFOOverflowError
from .exceptions import OkHardwareFIFOUnderflowError
from .exceptions import OkHardwareFileError
from .exceptions import OkHardwareI2CBitError
from .exceptions import OkHardwareI2CNackError
from .exceptions import OkHardwareI2CRestrictedAddressError
from .exceptions import OkHardwareI2CUnknownStatusError
from .exceptions import OkHardwareInvalidBitstreamError
from .exceptions import OkHardwareInvalidBlockSizeError
from .exceptions import OkHardwareInvalidEndpointError
from .exceptions import OkHardwareInvalidParameterError
from .exceptions import OkHardwareInvalidResetProfileError
from .exceptions import OkHardwareTimeoutError
from .exceptions import OkHardwareTransferError
from .exceptions import OkHardwareUnsupportedFeatureError
from .exceptions import OpalKellyBoardAlreadyInitializedError
from .exceptions import OpalKellyBoardNotInitializedError
from .exceptions import OpalKellyDataBlockNot32BytesError
from .exceptions import OpalKellyFileNotFoundError
from .exceptions import OpalKellyFrontPanelNotSupportedError
from .exceptions import OpalKellyHeaderNotEightBytesError
from .exceptions import OpalKellyIDGreaterThan32BytesError
from .exceptions import OpalKellyIncorrectHeaderError
from .exceptions import OpalKellyNoDeviceFoundError
from .exceptions import OpalKellySampleIdxNotFourBytesError
from .exceptions import OpalKellySpiAlreadyStartedError
from .exceptions import OpalKellySpiAlreadyStoppedError
from .exceptions import OpalKellyWordNotTwoBytesError
from .exceptions import parse_hardware_return_code
from .front_panel import FrontPanel
from .front_panel import FrontPanelBase
from .front_panel import FrontPanelSimulator
from .front_panel import validate_simulated_fifo_reads
from .main import activate_trigger_in
from .main import build_header_magic_number_bytes
from .main import check_file_exists
from .main import check_header
from .main import convert_sample_idx
from .main import convert_wire_value
from .main import convert_word
from .main import get_device_id
from .main import get_num_words_fifo
from .main import get_serial_number
from .main import initialize_board
from .main import is_pll_locked
from .main import is_spi_running
from .main import open_board
from .main import read_from_fifo
from .main import read_wire_out
from .main import reset_fifos
from .main import set_device_id
from .main import set_num_samples
from .main import set_run_mode
from .main import set_wire_in
from .main import start_acquisition
from .main import stop_acquisition
from .main import validate_device_id
from .ok import okCFrontPanel

__all__ = [
    "convert_sample_idx",
    "OpalKellySampleIdxNotFourBytesError",
    "convert_word",
    "OpalKellyWordNotTwoBytesError",
    "check_header",
    "OpalKellyHeaderNotEightBytesError",
    "start_acquisition",
    "parse_hardware_return_code",
    "OkHardwareInvalidEndpointError",
    "OkHardwareErrorNotRecognized",
    "OkHardwareDeviceNotOpenError",
    "TRIGGER_IN_SPI",
    "OpalKellyIncorrectHeaderError",
    "OpalKellyDataBlockNot32BytesError",
    "is_spi_running",
    "WIRE_OUT_IS_SPI_RUNNING",
    "HEADER_MAGIC_NUMBER",
    "set_run_mode",
    "WIRE_IN_RESET_MODE",
    "OkHardwareFailedError",
    "open_board",
    "OpalKellyNoDeviceFoundError",
    "get_num_words_fifo",
    "WIRE_OUT_NUM_WORDS_FIFO",
    "set_num_samples",
    "WIRE_IN_NUM_SAMPLES",
    "is_pll_locked",
    "WIRE_OUT_IS_PLL_LOCKED",
    "initialize_board",
    "read_wire_out",
    "OpalKellyFrontPanelNotSupportedError",
    "set_wire_in",
    "OkHardwareCommunicationError",
    "OkHardwareDataAlignmentError",
    "OkHardwareDoneNotHighError",
    "OkHardwareFIFOOverflowError",
    "OkHardwareFIFOUnderflowError",
    "OkHardwareI2CBitError",
    "OkHardwareI2CNackError",
    "OkHardwareI2CUnknownStatusError",
    "OkHardwareI2CRestrictedAddressError",
    "OkHardwareFileError",
    "OkHardwareTimeoutError",
    "OkHardwareInvalidBitstreamError",
    "OkHardwareInvalidBlockSizeError",
    "OkHardwareInvalidParameterError",
    "OkHardwareInvalidResetProfileError",
    "OkHardwareTransferError",
    "OkHardwareUnsupportedFeatureError",
    "okCFrontPanel",
    "FrontPanelBase",
    "FrontPanel",
    "FrontPanelSimulator",
    "OpalKellyBoardNotInitializedError",
    "main",
    "front_panel",
    "get_device_id",
    "set_device_id",
    "get_serial_number",
    "OpalKellyIDGreaterThan32BytesError",
    "stop_acquisition",
    "read_from_fifo",
    "BLOCK_SIZE",
    "PIPE_OUT_FIFO",
    "reset_fifos",
    "validate_device_id",
    "DATA_FRAME_SIZE_WORDS",
    "FPSimulatorInvalidFIFOValueError",
    "validate_simulated_fifo_reads",
    "build_header_magic_number_bytes",
    "OpalKellyBoardAlreadyInitializedError",
    "OpalKellySpiAlreadyStartedError",
    "OpalKellySpiAlreadyStoppedError",
    "check_file_exists",
    "OpalKellyFileNotFoundError",
    "DATA_FRAMES_PER_ROUND_ROBIN",
    "activate_trigger_in",
    "convert_wire_value",
]
