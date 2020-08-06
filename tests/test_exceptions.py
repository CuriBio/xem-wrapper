# -*- coding: utf-8 -*-
import pytest
from xem_wrapper import OkHardwareCommunicationError
from xem_wrapper import OkHardwareDataAlignmentError
from xem_wrapper import OkHardwareDeviceNotOpenError
from xem_wrapper import OkHardwareDoneNotHighError
from xem_wrapper import OkHardwareErrorNotRecognized
from xem_wrapper import OkHardwareFailedError
from xem_wrapper import OkHardwareFIFOOverflowError
from xem_wrapper import OkHardwareFIFOUnderflowError
from xem_wrapper import OkHardwareFileError
from xem_wrapper import OkHardwareI2CBitError
from xem_wrapper import OkHardwareI2CNackError
from xem_wrapper import OkHardwareI2CRestrictedAddressError
from xem_wrapper import OkHardwareI2CUnknownStatusError
from xem_wrapper import OkHardwareInvalidBitstreamError
from xem_wrapper import OkHardwareInvalidBlockSizeError
from xem_wrapper import OkHardwareInvalidEndpointError
from xem_wrapper import OkHardwareInvalidParameterError
from xem_wrapper import OkHardwareInvalidResetProfileError
from xem_wrapper import OkHardwareTimeoutError
from xem_wrapper import OkHardwareTransferError
from xem_wrapper import OkHardwareUnsupportedFeatureError
from xem_wrapper import parse_hardware_return_code


def test_parse_hardware_return_code__raises_no_error_on_0():
    assert parse_hardware_return_code(0) is None


def test_parse_hardware_return_code__raises_no_error_on_greater_than_zero():
    assert parse_hardware_return_code(1) is None


@pytest.mark.parametrize(
    "test_returned_value_from_hardware,expected_error,test_description",
    [
        (-1, OkHardwareFailedError, "failed"),
        (-2, OkHardwareTimeoutError, "timeout"),
        (-3, OkHardwareDoneNotHighError, "done not high"),
        (-4, OkHardwareTransferError, "transfer error"),
        (-5, OkHardwareCommunicationError, "communication error"),
        (-6, OkHardwareInvalidBitstreamError, "invalid bitstream"),
        (-7, OkHardwareFileError, "file error"),
        (-8, OkHardwareDeviceNotOpenError, "device not open"),
        (-9, OkHardwareInvalidEndpointError, "invalid endpoint"),
        (-10, OkHardwareInvalidBlockSizeError, "invalid block size"),
        (-11, OkHardwareI2CRestrictedAddressError, "I2C restricted address"),
        (-12, OkHardwareI2CBitError, "I2C bit error"),
        (-13, OkHardwareI2CNackError, "I2C nack error"),
        (-14, OkHardwareI2CUnknownStatusError, "I2C unknown status"),
        (-15, OkHardwareUnsupportedFeatureError, "unsupported feature"),
        (-16, OkHardwareFIFOUnderflowError, "FIFO underflow"),
        (-17, OkHardwareFIFOOverflowError, "FIFO overflow"),
        (-18, OkHardwareDataAlignmentError, "data alignment error"),
        (-19, OkHardwareInvalidResetProfileError, "invalid reset profile"),
        (-20, OkHardwareInvalidParameterError, "invalid parameter"),
        (-21, OkHardwareErrorNotRecognized, "an error we haven't handled yet"),
    ],
)
def test_parse_hardware_error__raises_appropriate_exceptions(
    test_returned_value_from_hardware, expected_error, test_description
):
    with pytest.raises(expected_error):
        parse_hardware_return_code(test_returned_value_from_hardware)
