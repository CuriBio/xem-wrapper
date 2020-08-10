# -*- coding: utf-8 -*-
"""Generic exceptions for Opal Kelly API."""


class OpalKellySampleIdxNotFourBytesError(Exception):
    pass


class OpalKellyWordNotTwoBytesError(Exception):
    pass


class OpalKellyHeaderNotEightBytesError(Exception):
    pass


class OpalKellyDataBlockNot32BytesError(Exception):
    pass


class OpalKellyIncorrectHeaderError(Exception):
    pass


class OpalKellyNoDeviceFoundError(Exception):
    pass


class OpalKellyFrontPanelNotSupportedError(Exception):
    pass


class OpalKellyIDGreaterThan32BytesError(Exception):
    pass


class OpalKellyFileNotFoundError(FileNotFoundError):
    pass


# Logical errors caught by the simulator/controller


class OpalKellyBoardAlreadyInitializedError(Exception):
    pass


class OpalKellyBoardNotInitializedError(Exception):
    pass


class OpalKellySpiAlreadyStartedError(Exception):
    pass


class OpalKellySpiAlreadyStoppedError(Exception):
    pass


class FPSimulatorInvalidFIFOValueError(Exception):
    pass


# Hardware errors


class OkHardwareErrorNotRecognized(Exception):
    pass


class OpalKellyHardwareError(Exception):
    pass


class OkHardwareFailedError(OpalKellyHardwareError):
    pass


class OkHardwareTimeoutError(OpalKellyHardwareError):
    pass


class OkHardwareDoneNotHighError(OpalKellyHardwareError):
    pass


class OkHardwareTransferError(OpalKellyHardwareError):
    pass


class OkHardwareCommunicationError(OpalKellyHardwareError):
    pass


class OkHardwareInvalidBitstreamError(OpalKellyHardwareError):
    pass


class OkHardwareFileError(OpalKellyHardwareError):
    pass


class OkHardwareDeviceNotOpenError(OpalKellyHardwareError):
    pass


class OkHardwareInvalidEndpointError(OpalKellyHardwareError):
    pass


class OkHardwareInvalidBlockSizeError(OpalKellyHardwareError):
    pass


class OkHardwareI2CRestrictedAddressError(OpalKellyHardwareError):
    pass


class OkHardwareI2CBitError(OpalKellyHardwareError):
    pass


class OkHardwareI2CNackError(OpalKellyHardwareError):
    pass


class OkHardwareI2CUnknownStatusError(OpalKellyHardwareError):
    pass


class OkHardwareUnsupportedFeatureError(OpalKellyHardwareError):
    pass


class OkHardwareFIFOUnderflowError(OpalKellyHardwareError):
    pass


class OkHardwareFIFOOverflowError(OpalKellyHardwareError):
    pass


class OkHardwareDataAlignmentError(OpalKellyHardwareError):
    pass


class OkHardwareInvalidResetProfileError(OpalKellyHardwareError):
    pass


class OkHardwareInvalidParameterError(OpalKellyHardwareError):
    pass


def parse_hardware_return_code(return_code: int) -> None:
    """Parse hardware return code and raise error if necessary.

    Args:
        return_code: integer value returned by OK API functions
    """
    if return_code >= 0:
        return
    if return_code == -1:
        raise OkHardwareFailedError()
    if return_code == -2:
        raise OkHardwareTimeoutError()
    if return_code == -3:
        raise OkHardwareDoneNotHighError()
    if return_code == -4:
        raise OkHardwareTransferError()
    if return_code == -5:
        raise OkHardwareCommunicationError()
    if return_code == -6:
        raise OkHardwareInvalidBitstreamError()
    if return_code == -7:
        raise OkHardwareFileError()
    if return_code == -8:
        raise OkHardwareDeviceNotOpenError()
    if return_code == -9:
        raise OkHardwareInvalidEndpointError()
    if return_code == -10:
        raise OkHardwareInvalidBlockSizeError()
    if return_code == -11:
        raise OkHardwareI2CRestrictedAddressError()
    if return_code == -12:
        raise OkHardwareI2CBitError()
    if return_code == -13:
        raise OkHardwareI2CNackError()
    if return_code == -14:
        raise OkHardwareI2CUnknownStatusError()
    if return_code == -15:
        raise OkHardwareUnsupportedFeatureError()
    if return_code == -16:
        raise OkHardwareFIFOUnderflowError()
    if return_code == -17:
        raise OkHardwareFIFOOverflowError()
    if return_code == -18:
        raise OkHardwareDataAlignmentError()
    if return_code == -19:
        raise OkHardwareInvalidResetProfileError()
    if return_code == -20:
        raise OkHardwareInvalidParameterError()

    raise OkHardwareErrorNotRecognized()
