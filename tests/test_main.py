# -*- coding: utf-8 -*-
import os
import struct

import pytest
from xem_wrapper import activate_trigger_in
from xem_wrapper import BLOCK_SIZE
from xem_wrapper import build_header_magic_number_bytes
from xem_wrapper import check_file_exists
from xem_wrapper import check_header
from xem_wrapper import convert_sample_idx
from xem_wrapper import convert_wire_value
from xem_wrapper import convert_word
from xem_wrapper import DATA_FRAME_SIZE_WORDS
from xem_wrapper import DATA_FRAMES_PER_ROUND_ROBIN
from xem_wrapper import get_device_id
from xem_wrapper import get_num_words_fifo
from xem_wrapper import get_serial_number
from xem_wrapper import HEADER_MAGIC_NUMBER
from xem_wrapper import initialize_board
from xem_wrapper import is_pll_locked
from xem_wrapper import is_spi_running
from xem_wrapper import main
from xem_wrapper import OkHardwareDeviceNotOpenError
from xem_wrapper import OkHardwareFailedError
from xem_wrapper import OkHardwareInvalidEndpointError
from xem_wrapper import OkHardwareUnsupportedFeatureError
from xem_wrapper import OpalKellyFileNotFoundError
from xem_wrapper import OpalKellyFrontPanelNotSupportedError
from xem_wrapper import OpalKellyHeaderNotEightBytesError
from xem_wrapper import OpalKellyIDGreaterThan32BytesError
from xem_wrapper import OpalKellyNoDeviceFoundError
from xem_wrapper import OpalKellySampleIdxNotFourBytesError
from xem_wrapper import OpalKellyWordNotTwoBytesError
from xem_wrapper import open_board
from xem_wrapper import PIPE_OUT_FIFO
from xem_wrapper import read_from_fifo
from xem_wrapper import read_wire_out
from xem_wrapper import reset_fifos
from xem_wrapper import set_device_id
from xem_wrapper import set_num_samples
from xem_wrapper import set_run_mode
from xem_wrapper import set_wire_in
from xem_wrapper import start_acquisition
from xem_wrapper import stop_acquisition
from xem_wrapper import TRIGGER_IN_SPI
from xem_wrapper import validate_device_id
from xem_wrapper import WIRE_IN_NUM_SAMPLES
from xem_wrapper import WIRE_IN_RESET_MODE
from xem_wrapper import WIRE_OUT_IS_PLL_LOCKED
from xem_wrapper import WIRE_OUT_IS_SPI_RUNNING
from xem_wrapper import WIRE_OUT_NUM_WORDS_FIFO
from xem_wrapper.main import FrontPanelDevices
from xem_wrapper.ok import okCFrontPanel
from xem_wrapper.ok import okTDeviceInfo

from .fixtures import fixture_test_bit_file_paths


__fixtures__ = [fixture_test_bit_file_paths]


def test_build_header_magic_number_bytes__returns_correct_bytearray_with_mantarray_header():

    expected_bytes = struct.pack(
        "<2L",
        (HEADER_MAGIC_NUMBER & 0xFFFFFFFF00000000) >> 32,
        HEADER_MAGIC_NUMBER & 0xFFFFFFFF,
    )

    actual = build_header_magic_number_bytes(HEADER_MAGIC_NUMBER)
    assert actual == expected_bytes


@pytest.mark.parametrize(
    "test_ep_addr,test_description",
    [
        (0x00, "calls methods correctly when ep_addr is 0x00"),
        (0x02, "calls methods correctly when ep_addr is 0x02"),
        (0xFF, "calls methods correctly when ep_addr is 0xFF"),
    ],
)
def test_read_wire_out__xem_methods_called_with_correct_signature(
    test_ep_addr, test_description, mocker
):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_update_method = mocker.patch.object(
        dummy_xem, "UpdateWireOuts", autospec=True, return_value=0
    )
    mocked_get_method = mocker.patch.object(
        dummy_xem, "GetWireOutValue", autospec=True, return_value=0
    )
    read_wire_out(dummy_xem, test_ep_addr)

    mocked_update_method.assert_called_once_with()
    mocked_get_method.assert_called_once_with(test_ep_addr)


@pytest.mark.parametrize(
    "test_mock_get_value,test_ep_addr,expected,test_description",
    [
        (0x00000000, 0x00, 0x00000000, "0x0000000 returns 0x0000000"),
        (0xFFFFFFFE, 0x00, 0xFFFFFFFE, "0xFFFFFFFE returns 0xFFFFFFFE"),
        (0x00000001, 0x00, 0x00000001, "0x00000001 returns 0x00000001"),
        (0xFFFFFFFF, 0x00, 0xFFFFFFFF, "0xFFFFFFFF returns 0xFFFFFFFF"),
    ],
)
def test_read_wire_out__returns_expected_values(
    test_mock_get_value, test_ep_addr, expected, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "UpdateWireOuts", autospec=True, return_value=0)
    mocker.patch.object(
        dummy_xem, "GetWireOutValue", autospec=True, return_value=test_mock_get_value
    )
    result = read_wire_out(dummy_xem, test_ep_addr)

    assert result == expected


def test_read_wire_out__xem_methods_called_in_correct_order(mocker):
    dummy_xem = okCFrontPanel()
    mocked_get_method = mocker.patch.object(
        dummy_xem, "GetWireOutValue", autospec=True, return_value=0
    )

    # create side effect to raise error if methods called in incorrect order
    def side_effect(*args, **kwargs):
        mocked_get_method.assert_not_called()
        return 0

    mocker.patch.object(
        dummy_xem, "UpdateWireOuts", autospec=True, side_effect=side_effect
    )

    read_wire_out(dummy_xem, 0x00)


@pytest.mark.parametrize(
    "test_mock_update_value,test_mock_get_value,expected_error,test_description",
    [
        (-8, 0, OkHardwareDeviceNotOpenError, "raises error when device is not open"),
        (0, -1, OkHardwareFailedError, "raises error when operation fails"),
    ],
)
def test_read_wire_out__raises_correct_error(
    test_mock_update_value,
    test_mock_get_value,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "UpdateWireOuts", autospec=True, return_value=test_mock_update_value
    )
    mocker.patch.object(
        dummy_xem, "GetWireOutValue", autospec=True, return_value=test_mock_get_value
    )
    with pytest.raises(expected_error):
        read_wire_out(dummy_xem, 0x00)


@pytest.mark.parametrize(
    "test_sample_idx_byte_array,expected,test_description",
    [
        (bytearray([0, 0, 0, 0]), 0, "zero returns zero"),
        (bytearray([1, 0, 0, 0]), 1, "one returns one"),
        (
            bytearray([255, 255, 255, 255]),
            4294967295,
            "four max bytes return 4294967295",
        ),
        (bytearray([255, 255, 255, 127]), 2147483647, "2147483647 returns 2147483647"),
    ],
)
def test_convert_sample_idx__returns_expected_values(
    test_sample_idx_byte_array, expected, test_description
):
    result = convert_sample_idx(test_sample_idx_byte_array)

    assert result == expected


def test_convert_sample_idx__raises_error_if_length_of_input_array_is_greater_than_4():
    with pytest.raises(OpalKellySampleIdxNotFourBytesError):
        convert_sample_idx(bytearray(5))


@pytest.mark.parametrize(
    "test_word_byte_array,expected,test_description",
    [
        (bytearray([0, 0]), 0, "zero returns zero"),
        (bytearray([1, 0]), 1, "one returns one"),
        (bytearray([255, 255]), 65535, "two max bytes return 65535"),
        (bytearray([255, 127]), 32767, "32767 returns 32767"),
    ],
)
def test_convert_word__returns_expected_values(
    test_word_byte_array, expected, test_description
):
    result = convert_word(test_word_byte_array)

    assert result == expected


def test_convert_word__raises_error_if_length_of_input_array_is_greater_than_2():
    with pytest.raises(OpalKellyWordNotTwoBytesError):
        convert_word(bytearray(3))


@pytest.mark.parametrize(
    "test_wire_val,expected_converted_val,test_description",
    [
        (0x000000AB, 0xAB000000, "converts 0x000000AB to 0xAB000000"),
        (0xDC000000, 0x000000DC, "converts 0xDC000000 to 0x000000DC"),
        (0x12345678, 0x78563412, "converts 0x12345678 to 0x78563412"),
    ],
)
def test_convert_wire_value__returns_correct_values(
    test_wire_val, expected_converted_val, test_description
):
    actual = convert_wire_value(test_wire_val)
    assert actual == expected_converted_val


@pytest.mark.parametrize(
    "test_header_byte_array,expected,test_description",
    [
        (bytearray([0, 0, 0, 0, 0, 0, 0, 0]), False, "zero returns false"),
        (bytearray([1, 0, 0, 0, 0, 0, 0, 0]), False, "one returns false"),
        (
            bytearray([255, 255, 255, 255, 255, 255, 255, 255]),
            False,
            "eight max bytes return false",
        ),
        (
            build_header_magic_number_bytes(HEADER_MAGIC_NUMBER),
            True,
            "0xc691199927021942 returns true",
        ),
    ],
)
def test_check_header__returns_expected_values(
    test_header_byte_array, expected, test_description
):
    result = check_header(test_header_byte_array)

    assert result == expected


def test_check_header__raises_error_if_length_of_input_array_is_greater_than_8():
    with pytest.raises(OpalKellyHeaderNotEightBytesError):
        check_header(bytearray(9))


def test_start_acquisition__methods_called_with_correct_signature(mocker):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_activate_method = mocker.patch.object(
        main, "activate_trigger_in", autospec=True
    )
    start_acquisition(dummy_xem)

    mocked_activate_method.assert_called_once_with(dummy_xem, TRIGGER_IN_SPI, 0)


def test_start_acquisition__raises_error_when_device_returns_invalid_endpoint(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "ActivateTriggerIn", autospec=True, return_value=-9)
    with pytest.raises(OkHardwareInvalidEndpointError):
        start_acquisition(dummy_xem)


def test_is_spi_running__read_method_called_with_correct_signature(mocker):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_read_method = mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=0
    )
    is_spi_running(dummy_xem)

    mocked_read_method.assert_called_once_with(dummy_xem, WIRE_OUT_IS_SPI_RUNNING)


@pytest.mark.parametrize(
    "test_read_value,expected,test_description",
    [(0, False, "zero returns false"), (1, True, "one returns true")],
)
def test_is_spi_running__returns_expected_values(
    test_read_value, expected, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=test_read_value
    )

    assert is_spi_running(dummy_xem) is expected


def test_is_pll_locked__read_method_called_with_correct_signature(mocker):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_read_method = mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=0
    )
    is_pll_locked(dummy_xem)

    mocked_read_method.assert_called_once_with(dummy_xem, WIRE_OUT_IS_PLL_LOCKED)


@pytest.mark.parametrize(
    "test_read_value,expected_status,test_description",
    [
        (0x00000000, False, "0x0000000 returns false"),
        (0xFFFFFFFE, False, "0xFFFFFFFE returns false"),
        (0x00000001, True, "0x00000001 returns true"),
        (0xFFFFFFFF, True, "0xFFFFFFFF returns true"),
    ],
)
def test_is_pll_locked__returns_expected_values(
    test_read_value, expected_status, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=test_read_value
    )

    assert is_pll_locked(dummy_xem) is expected_status


@pytest.mark.parametrize(
    "test_run_mode,expected_run_mode_bit_value,test_description",
    [
        (True, 0x00000002, "calls methods correctly when set continuous"),
        (False, 0x00000000, "calls methods correctly when set noncontinuous"),
    ],
)
def test_set_run_mode__xem_methods_called_with_correct_signature(
    test_run_mode, expected_run_mode_bit_value, test_description, mocker
):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_set_method = mocker.patch.object(main, "set_wire_in", autospec=True)

    set_run_mode(dummy_xem, test_run_mode)

    mocked_set_method.assert_called_once_with(
        dummy_xem, WIRE_IN_RESET_MODE, expected_run_mode_bit_value, 0x00000002
    )


@pytest.mark.parametrize(
    "test_mock_set_value,test_mock_update_value,expected_error,test_description",
    [
        (-8, 0, OkHardwareDeviceNotOpenError, "raises error when device is not open"),
        (0, -1, OkHardwareFailedError, "raises error when operation fails"),
    ],
)
def test_set_run_mode__raises_correct_error(
    test_mock_set_value,
    test_mock_update_value,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "SetWireInValue", autospec=True, return_value=test_mock_set_value
    )
    mocker.patch.object(
        dummy_xem, "UpdateWireIns", autospec=True, return_value=test_mock_update_value
    )
    with pytest.raises(expected_error):
        set_run_mode(dummy_xem, True)


@pytest.mark.parametrize(
    "test_num_samples,test_description",
    [
        (0x00000000, "calls methods correctly with 0x00000000"),
        (0x00010001, "calls methods correctly with 0x00010001"),
        (0xA000000A, "calls methods correctly with 0xA000000A"),
        (0x00088000, "calls methods correctly with 0x00088000"),
        (0xFFFFFFFF, "calls methods correctly with 0xFFFFFFFF"),
    ],
)
def test_set_num_samples__xem_methods_called_with_correct_signature(
    test_num_samples,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocked_set_method = mocker.patch.object(main, "set_wire_in", autospec=True)

    set_num_samples(dummy_xem, test_num_samples)

    mocked_set_method.assert_called_once_with(
        dummy_xem, WIRE_IN_NUM_SAMPLES, test_num_samples, 0xFFFFFFFF
    )


@pytest.mark.parametrize(
    "test_file_name,test_description",
    [
        ("", "calls methods correctly with empty string."),
        ("test.bit", "calls methods correctly with 'test.bit' string."),
    ],
)
def test_initialize_board__xem_methods_called_with_correct_signature(
    test_file_name, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocked_configure_method = mocker.patch.object(
        dummy_xem, "ConfigureFPGA", autospec=True, return_value=0
    )
    mocked_enabled_method = mocker.patch.object(
        dummy_xem, "IsFrontPanelEnabled", autospec=True, return_value=True
    )
    mocked_check_method = mocker.patch.object(main, "check_file_exists", autospec=True)
    initialize_board(dummy_xem, bit_file_name=test_file_name)

    mocked_configure_method.assert_called_once_with(test_file_name)
    mocked_enabled_method.assert_called_once_with()
    mocked_check_method.assert_called_once_with(test_file_name)


def test_initialize_board__no_bit_file_loaded_if_not_supplied(mocker):
    dummy_xem = okCFrontPanel()
    mocked_configure_method = mocker.patch.object(
        dummy_xem, "ConfigureFPGA", autospec=True, return_value=0
    )
    mocked_enabled_method = mocker.patch.object(
        dummy_xem, "IsFrontPanelEnabled", autospec=True, return_value=True
    )
    initialize_board(dummy_xem)

    assert mocked_configure_method.call_count == 0
    mocked_enabled_method.assert_called_once_with()


@pytest.mark.parametrize(
    """test_mock_configure_value,test_mock_enabled_value,test_mock_check_side_effect,
    expected_error,test_description""",
    [
        (-1, True, None, OkHardwareFailedError, "raises error when operation fails"),
        (
            0,
            False,
            None,
            OpalKellyFrontPanelNotSupportedError,
            "raises error when front panel isn't supported",
        ),
        (
            0,
            False,
            OpalKellyFileNotFoundError(),
            OpalKellyFileNotFoundError,
            "raises error when file is not found",
        ),
    ],
)
def test_initialize_board__raises_correct_errors(
    test_mock_configure_value,
    test_mock_enabled_value,
    test_mock_check_side_effect,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem,
        "ConfigureFPGA",
        autospec=True,
        return_value=test_mock_configure_value,
    )
    mocker.patch.object(
        dummy_xem,
        "IsFrontPanelEnabled",
        autospec=True,
        return_value=test_mock_enabled_value,
    )
    mocker.patch.object(
        main,
        "check_file_exists",
        autospec=True,
        side_effect=test_mock_check_side_effect,
    )
    with pytest.raises(expected_error):
        initialize_board(dummy_xem, "test.bit")


def test_open_board__returns_xem_as_front_panel_object_if_device_is_connected(mocker):
    expected_xem = okCFrontPanel()
    mocker.patch.object(
        FrontPanelDevices, "Open", autospec=True, return_value=expected_xem
    )
    actual_xem = open_board()
    assert actual_xem is expected_xem


def test_open_board__raises_error_if_no_device_is_found(mocker):
    mocker.patch.object(FrontPanelDevices, "Open", autospec=True, return_value=None)
    with pytest.raises(OpalKellyNoDeviceFoundError):
        open_board()


@pytest.mark.parametrize(
    "test_read_value, expected_num_words_fifo, test_description",
    [
        (0, 0, "zero return zero"),
        (1, 1, "one returns 1"),
        (0xFFFF, 0xFFFF, "0xFFFF returns 0xFFFF"),
    ],
)
def test_get_num_words_fifo__returns_expected_values(
    test_read_value, expected_num_words_fifo, test_description, mocker
):
    dummy_xem = okCFrontPanel()

    mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=test_read_value
    )

    result = get_num_words_fifo(dummy_xem)
    assert result == expected_num_words_fifo


def test_get_num_words_fifo__read_method_called_with_correct_signature(mocker):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_read_method = mocker.patch.object(
        main, "read_wire_out", autospec=True, return_value=0
    )
    get_num_words_fifo(dummy_xem)

    mocked_read_method.assert_called_once_with(dummy_xem, WIRE_OUT_NUM_WORDS_FIFO)


@pytest.mark.parametrize(
    "test_addr,test_value,test_mask,test_description",
    [
        (
            0x00,
            0x00000000,
            0x0000000,
            "calls methods correctly with addr 0x00, value 0x00000000, mask 0x00000000",
        ),
        (
            0xFF,
            0x00000000,
            0x0000000,
            "calls methods correctly with addr 0xFF, value 0x00000000, mask 0x00000000",
        ),
        (
            0x00,
            0x00000001,
            0x0000000,
            "calls methods correctly with addr 0x00, value 0x00000001, mask 0x00000000",
        ),
        (
            0x00,
            0x00000000,
            0x0000001,
            "calls methods correctly with addr 0x00, value 0x00000000, mask 0x00000001",
        ),
        (
            0x00,
            0x00000001,
            0x0000001,
            "calls methods correctly with addr 0x00, value 0x00000001, mask 0x00000001",
        ),
    ],
)
def test_set_wire_in__calls_methods_with_expected_values(
    test_addr, test_value, test_mask, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocked_set_method = mocker.patch.object(
        dummy_xem, "SetWireInValue", autospec=True, return_value=0
    )
    mocked_update_method = mocker.patch.object(
        dummy_xem, "UpdateWireIns", autospec=True, return_value=0
    )

    set_wire_in(dummy_xem, test_addr, test_value, test_mask)

    mocked_set_method.assert_called_once_with(test_addr, test_value, test_mask)
    mocked_update_method.assert_called_once_with()


@pytest.mark.parametrize(
    "test_mock_set_value,test_mock_update_value,expected_error,test_description",
    [
        (
            -9,
            0,
            OkHardwareInvalidEndpointError,
            "raises error when an invalid endpoint is called",
        ),
        (0, -1, OkHardwareFailedError, "raises error when operation fails"),
    ],
)
def test_set_wire_in__raises_correct_errors(
    test_mock_set_value,
    test_mock_update_value,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "SetWireInValue", autospec=True, return_value=test_mock_set_value
    )
    mocker.patch.object(
        dummy_xem, "UpdateWireIns", autospec=True, return_value=test_mock_update_value
    )

    with pytest.raises(expected_error):
        set_wire_in(dummy_xem, 0x00, 0x00000000, 0x0000000)


def test_set_wire_in__xem_methods_called_in_correct_order(mocker):
    dummy_xem = okCFrontPanel()
    mocked_update_method = mocker.patch.object(
        dummy_xem, "UpdateWireIns", autospec=True, return_value=0
    )

    # create side effect to raise error if methods called in incorrect order
    def side_effect(*args, **kwargs):
        mocked_update_method.assert_not_called()
        return 0

    mocker.patch.object(
        dummy_xem, "SetWireInValue", autospec=True, side_effect=side_effect
    )

    set_wire_in(dummy_xem, 0x00, 0x00000000, 0x0000000)


def test_get_device_id__calls_methods_with_correct_signature(mocker):
    dummy_info = okTDeviceInfo()
    mocker.patch.object(main, "okTDeviceInfo", autospec=True, return_value=dummy_info)

    dummy_xem = okCFrontPanel()
    mocked_get_method = mocker.patch.object(
        dummy_xem, "GetDeviceInfo", autospec=True, return_value=0
    )

    get_device_id(dummy_xem)

    mocked_get_method.assert_called_once_with(dummy_info)


@pytest.mark.parametrize(
    "expected_id,test_description",
    [
        ("Mantarray XEM7310", "correctly returns id: Mantarray XEM7310"),
        ("", "correctly returns empty id string"),
    ],
)
def test_get_device_id__returns_expected_values(expected_id, test_description, mocker):
    dummy_info = okTDeviceInfo()
    dummy_info.deviceID = expected_id
    mocker.patch.object(main, "okTDeviceInfo", autospec=True, return_value=dummy_info)

    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "GetDeviceInfo", autospec=True, return_value=0)

    result = get_device_id(dummy_xem)

    assert result == expected_id


def test_get_device_id__raises_correct_error(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "GetDeviceInfo", autospec=True, return_value=-8)

    with pytest.raises(OkHardwareDeviceNotOpenError):
        get_device_id(dummy_xem)


@pytest.mark.parametrize(
    "test_id,test_description",
    [
        ("Mantarray XEM7310", "correctly sets new id: Mantarray XEM7310"),
        ("", "correctly sets id to emtpy string"),
    ],
)
def test_set_device_id__calls_method_with_correct_signature(
    test_id, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocked_set_method = mocker.patch.object(
        dummy_xem, "SetDeviceID", autospec=True, return_value=0
    )

    set_device_id(dummy_xem, test_id)

    mocked_set_method.assert_called_once_with(test_id)


def test_set_device_id__raises_correct_error(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "SetDeviceID", autospec=True, return_value=-8)

    with pytest.raises(OkHardwareDeviceNotOpenError):
        set_device_id(dummy_xem, "")


@pytest.mark.parametrize(
    "test_id,test_description",
    [
        (
            "123456789012345678901234567890123",
            "raises error when string exceeds byte length with ascii chars",
        ),
        (
            "ááááááááááááááááá",
            "raises error when string exceeds byte length with unicode chars",
        ),
        (
            "ááááááááááááááááA",
            "raises error when string exceeds byte length with ascii and unicode chars",
        ),
    ],
)
def test_set_device_id__raises_OpalKellyIDGreaterThan32BytesError_correctly(
    test_id, test_description, mocker
):
    with pytest.raises(OpalKellyIDGreaterThan32BytesError):
        validate_device_id(test_id)


def test_get_serial_number__calls_methods_with_correct_signature(mocker):
    dummy_info = okTDeviceInfo()
    mocker.patch.object(main, "okTDeviceInfo", autospec=True, return_value=dummy_info)

    dummy_xem = okCFrontPanel()
    mocked_get_method = mocker.patch.object(
        dummy_xem, "GetDeviceInfo", autospec=True, return_value=0
    )

    get_serial_number(dummy_xem)

    mocked_get_method.assert_called_once_with(dummy_info)


@pytest.mark.parametrize(
    "expected_serial_number,test_description",
    [
        ("1917000Q7O", "correctly returns serial number: "),
        ("", "correctly returns empty serial number"),
    ],
)
def test_get_serial_number__returns_expected_values(
    expected_serial_number, test_description, mocker
):
    dummy_info = okTDeviceInfo()
    dummy_info.serialNumber = expected_serial_number
    mocker.patch.object(main, "okTDeviceInfo", autospec=True, return_value=dummy_info)

    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "GetDeviceInfo", autospec=True, return_value=0)

    result = get_serial_number(dummy_xem)

    assert result == expected_serial_number


def test_serial_number__raises_correct_error(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "GetDeviceInfo", autospec=True, return_value=-8)

    with pytest.raises(OkHardwareDeviceNotOpenError):
        get_serial_number(dummy_xem)


def test_stop_acquisition__methods_called_with_correct_signature(mocker):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_activate_method = mocker.patch.object(
        main, "activate_trigger_in", autospec=True, return_value=0
    )
    stop_acquisition(dummy_xem)

    mocked_activate_method.assert_called_once_with(dummy_xem, TRIGGER_IN_SPI, 1)


def test_stop_acquisition__raises_error_when_device_returns_invalid_endpoint(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(dummy_xem, "ActivateTriggerIn", autospec=True, return_value=-9)
    with pytest.raises(OkHardwareInvalidEndpointError):
        stop_acquisition(dummy_xem)


@pytest.mark.parametrize(
    "test_num_words,expected_read_buffer_size,test_description",
    [
        (0, 0, "calls methods correctly with no words in FIFO"),
        (71, 0, "calls methods correctly with 71 words in FIFO"),
        (72, 288, "calls methods correctly with 72 words in FIFO"),
        (80, 288, "calls methods correctly with 80 words in FIFO"),
        (143, 288, "calls methods correctly with 143 words in FIFO"),
        (144, 576, "calls methods correctly with 144 words in FIFO"),
    ],
)
def test_read_from_fifo__calls_methods_with_correct_signature(
    test_num_words, expected_read_buffer_size, test_description, mocker
):
    dummy_xem = okCFrontPanel()

    mocked_get_method = mocker.patch.object(
        main, "get_num_words_fifo", autospec=True, return_value=test_num_words
    )
    mocked_set_method = mocker.patch.object(main, "set_wire_in", autospec=True)
    mocked_read_method = mocker.patch.object(
        dummy_xem, "ReadFromBlockPipeOut", autospec=True, return_value=0
    )

    read_from_fifo(dummy_xem)

    mocked_get_method.assert_called_once_with(dummy_xem)
    if test_num_words >= 72:
        mocked_set_method.assert_has_calls(
            (
                mocker.call(dummy_xem, WIRE_IN_RESET_MODE, 0x0002, 0x0002),
                mocker.call(dummy_xem, WIRE_IN_RESET_MODE, 0x0000, 0x0002),
            ),
        )
        mocked_read_method.assert_called_once_with(
            PIPE_OUT_FIFO, BLOCK_SIZE, bytearray(expected_read_buffer_size)
        )


@pytest.mark.parametrize(
    "test_data,test_description",
    [
        (
            bytearray(DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN * 4),
            "returns correct value with empty bytearray",
        ),
        (
            bytearray([1] * (DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN * 4)),
            "returns correct value with bytearray of ones",
        ),
        (
            bytearray(
                [
                    i % 256
                    for i in range(
                        DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN * 4
                    )
                ]
            ),
            "returns correct value with bytearray incremental values",
        ),
    ],
)
def test_read_from_fifo__returns_correct_values(test_data, test_description, mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        main,
        "get_num_words_fifo",
        autospec=True,
        return_value=DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN,
    )
    mocker.patch.object(main, "reset_fifos", autospec=True)
    mocker.patch.object(main, "set_wire_in", autospec=True)

    def side_effect(*args, **kwargs):
        args[2][:] = test_data[:]
        return 0

    mocker.patch.object(
        dummy_xem, "ReadFromBlockPipeOut", autospec=True, side_effect=side_effect
    )

    result = read_from_fifo(dummy_xem)

    assert result == test_data


@pytest.mark.parametrize(
    "test_num_words,test_description",
    [
        (0, "returns emtpy bytearray with no words"),
        (
            DATA_FRAME_SIZE_WORDS - 1,
            "returns empty array when one word short of data frame size",
        ),
    ],
)
def test_read_from_fifo__returns_empty_array_if_size_of_num_words_is_less_required(
    test_num_words, test_description, mocker
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "ReadFromBlockPipeOut", autospec=True, return_value=0
    )

    mocker.patch.object(
        main, "get_num_words_fifo", autospec=True, return_value=test_num_words
    )
    mocker.patch.object(main, "reset_fifos", autospec=True)
    mocker.patch.object(main, "set_wire_in", autospec=True)

    result = read_from_fifo(dummy_xem)

    expected = bytearray(0)
    assert result == expected


def test_read_from_fifo__raises_error_when_device_returns_unsupported_feature(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "ReadFromBlockPipeOut", autospec=True, return_value=-15
    )

    mocker.patch.object(
        main,
        "get_num_words_fifo",
        autospec=True,
        return_value=DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN,
    )
    mocker.patch.object(main, "reset_fifos", autospec=True)
    mocker.patch.object(main, "set_wire_in", autospec=True)
    with pytest.raises(OkHardwareUnsupportedFeatureError):
        read_from_fifo(dummy_xem)


def test_reset_fifos__calls_methods_with_correct_signature(mocker):
    dummy_xem = okCFrontPanel()
    mocked_set_method = mocker.patch.object(main, "set_wire_in", autospec=True)
    reset_fifos(dummy_xem)

    mocked_set_method.assert_has_calls(
        (
            mocker.call(dummy_xem, 0x00, 0x0004, 0x0004),
            mocker.call(dummy_xem, 0x00, 0x0000, 0x0004),
        )
    )


@pytest.mark.parametrize(
    "test_mock_set_value,test_mock_update_value,expected_error,test_description",
    [
        (-8, 0, OkHardwareDeviceNotOpenError, "raises error when device is not open"),
        (0, -1, OkHardwareFailedError, "raises error when operation fails"),
    ],
)
def test_reset_fifos__raises_correct_errors(
    test_mock_set_value,
    test_mock_update_value,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem, "SetWireInValue", autospec=True, return_value=test_mock_set_value
    )
    mocker.patch.object(
        dummy_xem, "UpdateWireIns", autospec=True, return_value=test_mock_update_value
    )

    with pytest.raises(expected_error):
        reset_fifos(dummy_xem)


def test_check_file_exists__raises_error_if_file_does_not_exist(mocker):
    test_file_name = "fake_file.txt"
    with pytest.raises(OpalKellyFileNotFoundError) as exc_info:
        check_file_exists(test_file_name)
    assert test_file_name in exc_info.value.args[0]
    assert os.getcwd() in exc_info.value.args[0]


def test_check_file_exists__does_not_raise_error_if_file_exists(
    mocker, test_bit_file_paths
):
    test_file_name = test_bit_file_paths[0]
    mocked_isfile = mocker.spy(os.path, "isfile")
    check_file_exists(test_file_name)

    mocked_isfile.assert_called_once_with(test_file_name)


@pytest.mark.parametrize(
    """test_ep_addr,test_bit,test_description""",
    [
        (0x00, 0x00, "activates bit 0 on trig 0"),
        (0xFF, 0x00, "activates bit 0 on trig FF"),
        (0x00, 0x80000000, "activates bit 32 on trig 0"),
        (0xFF, 0x80000000, "activates bit 32 on trig FF"),
    ],
)
def test_activate_trigger_in__calls_method_with_correct_signature(
    test_ep_addr, test_bit, test_description, mocker
):
    # would raise error if test failed
    dummy_xem = okCFrontPanel()
    mocked_activate_method = mocker.patch.object(
        dummy_xem, "ActivateTriggerIn", autospec=True, return_value=0
    )
    activate_trigger_in(dummy_xem, test_ep_addr, test_bit)

    mocked_activate_method.assert_called_once_with(test_ep_addr, test_bit)


@pytest.mark.parametrize(
    "test_mock_activate_value,expected_error,test_description",
    [
        (
            -9,
            OkHardwareInvalidEndpointError,
            "raises error when an invalid endpoint is called",
        ),
        (-1, OkHardwareFailedError, "raises error when operation fails"),
    ],
)
def test_activate_trigger_in__raises_correct_errors(
    test_mock_activate_value,
    expected_error,
    test_description,
    mocker,
):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(
        dummy_xem,
        "ActivateTriggerIn",
        autospec=True,
        return_value=test_mock_activate_value,
    )

    with pytest.raises(expected_error):
        activate_trigger_in(dummy_xem, 0x00, 0x00)
