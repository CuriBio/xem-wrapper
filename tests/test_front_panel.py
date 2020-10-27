# -*- coding: utf-8 -*-
import multiprocessing
import os

import pytest
from stdlib_utils import is_queue_eventually_empty
from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import SimpleMultiprocessingQueue
from xem_wrapper import DATA_FRAME_SIZE_WORDS
from xem_wrapper import DATA_FRAMES_PER_ROUND_ROBIN
from xem_wrapper import FPSimulatorInvalidFIFOValueError
from xem_wrapper import front_panel
from xem_wrapper import FrontPanel
from xem_wrapper import FrontPanelBase
from xem_wrapper import FrontPanelSimulator
from xem_wrapper import okCFrontPanel
from xem_wrapper import OpalKellyBoardAlreadyInitializedError
from xem_wrapper import OpalKellyBoardNotInitializedError
from xem_wrapper import OpalKellyFileNotFoundError
from xem_wrapper import OpalKellyIDGreaterThan32BytesError
from xem_wrapper import OpalKellySpiAlreadyStartedError
from xem_wrapper import OpalKellySpiAlreadyStoppedError
from xem_wrapper import PIPE_OUT_FIFO
from xem_wrapper import validate_simulated_fifo_reads

from .fixtures import fixture_initialized_front_panel_with_dummy_xem
from .fixtures import fixture_test_bit_file_paths

__fixtures__ = [
    fixture_initialized_front_panel_with_dummy_xem,
    fixture_test_bit_file_paths,
]


# function tests
@pytest.mark.parametrize(
    "test_read,test_description",
    [
        (bytearray(1), "raises error when given data read of size one"),
        (
            bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN - 1),
            "raises error when given data read one byte short of valid size",
        ),
        (
            bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN + 1),
            "raises error when given data read one byte over valid size",
        ),
    ],
)
def test_validate_simulated_fifo_reads__raises_error_when_passed_single_invalid_data_size(
    test_read, test_description
):
    fifo = SimpleMultiprocessingQueue()
    fifo.put(test_read)
    with pytest.raises(FPSimulatorInvalidFIFOValueError):
        validate_simulated_fifo_reads(fifo)


def test_validate_simulated_fifo_reads__correctly_checks_empty_fifo():
    fifo = SimpleMultiprocessingQueue()
    validate_simulated_fifo_reads(fifo)

    assert fifo.empty() is True


def test_validate_simulated_fifo_reads__raises_error_if_queue_contains_invalid_data_size():
    fifo = SimpleMultiprocessingQueue()
    test_reads = [
        bytearray(0),
        bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN),
        bytearray(2),
    ]
    for data_read in test_reads:
        fifo.put(data_read)
    with pytest.raises(FPSimulatorInvalidFIFOValueError):
        validate_simulated_fifo_reads(fifo)


# FrontPanelBase tests
def test_FrontPanelBase_class_attributes():
    assert FrontPanelBase.default_xem_serial_number == "1917000Q70"


def test_FrontPanelBase__has_hard_stop_method_with_same_signature_as_stdlib_utils_InfiniteLoopingParallelismMixIn():
    fp = FrontPanelBase()
    actual = fp.hard_stop()
    assert isinstance(actual, dict) is True

    # can accept a kwarg for timeout without raising an error
    fp.hard_stop(timeout=5.5)


def test_FrontPanelBase__initialize_board__sets_internal_board_state():
    fp = FrontPanelBase()
    assert fp.is_board_initialized() is False
    fp.initialize_board()
    assert fp.is_board_initialized() is True


def test_FrontPanelBase__initialize_board__sets_internal_bit_file_name(
    test_bit_file_paths,
):
    fp = FrontPanelBase()
    expected_bit_file_name = test_bit_file_paths[0]
    assert fp.get_bit_file_name() is None
    fp.initialize_board(bit_file_name=expected_bit_file_name)
    assert fp.get_bit_file_name() == expected_bit_file_name


def test_FrontPanelBase__initialize_board__raises_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.is_board_initialized() is True
    with pytest.raises(OpalKellyBoardAlreadyInitializedError):
        fp.initialize_board()


def test_FrontPanelBase__initialize_board__allow_board_reinitialization_kwarg_suppresses_error(
    test_bit_file_paths,
):
    fp = FrontPanelBase()
    fp.initialize_board(bit_file_name=test_bit_file_paths[0])
    assert fp.get_bit_file_name() == test_bit_file_paths[0]
    assert fp.is_board_initialized() is True
    fp.initialize_board(
        bit_file_name=test_bit_file_paths[1], allow_board_reinitialization=True
    )
    assert fp.get_bit_file_name() == test_bit_file_paths[1]


def test_FrontPanelBase__initialize_board__raises_error_if_bit_file_does_not_exist():
    fp = FrontPanelBase()
    expected_path = "fake_folder/fake_file.bit"
    with pytest.raises(OpalKellyFileNotFoundError) as exc_info:
        fp.initialize_board(bit_file_name=expected_path)
    assert expected_path in exc_info.value.args[0]
    assert os.getcwd() in exc_info.value.args[0]


def test_FrontPanelBase__read_wire_out__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_wire_out(1)


def test_FrontPanelBase__read_wire_out__does_not_raise_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert (
        fp.read_wire_out(1) == 0
    )  # the base function just always returns 0. Subclass implementations can return meaningful values


def test_FrontPanelBase__set_device_id__raises_error_if_id_is_too_many_bytes(mocker):
    fp = FrontPanelBase()
    new_id = "123456789012345678901234567890123"
    with pytest.raises(OpalKellyIDGreaterThan32BytesError):
        fp.set_device_id(new_id)


def test_FrontPanelBase__read_from_fifo__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_from_fifo()


def test_FrontPanelBase__read_from_fifo__does_not_raise_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.read_from_fifo() == bytearray(
        0
    )  # the base function just always returns an empty bytearray. Subclass implementations can return meaningful values


def test_FrontPanelBase__get_num_words_fifo__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.get_num_words_fifo()


def test_FrontPanelBase__get_num_words_fifo__does_not_raise_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert (
        fp.get_num_words_fifo() == 0
    )  # the base function just always returns 0. Subclass implementations can return meaningful values


def test_FrontPanelBase__get_internal_spi_running_status__does_not_raise_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.get_internal_spi_running_status() is False


def test_FrontPanelBase__is_spi_running__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.is_spi_running()


def test_FrontPanelBase__is_spi_running__does_not_raise_error_if_board_initialized():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.is_spi_running() is False


def test_FrontPanelBase__start_acquisition__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.start_acquisition()


def test_FrontPanelBase__start_acquisition__raises_error_if_spi_already_started():
    fp = FrontPanelBase()
    fp.initialize_board()
    fp.start_acquisition()
    assert fp.is_spi_running() is True
    with pytest.raises(OpalKellySpiAlreadyStartedError):
        fp.start_acquisition()


def test_FrontPanelBase__start_acquisition__sets_internal_spi_running_state():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.is_spi_running() is False
    fp.start_acquisition()
    assert fp.is_spi_running() is True


def test_FrontPanelBase__stop_acquisition__raises_error_if_board_not_initialized():
    fp = FrontPanelBase()
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.stop_acquisition()


def test_FrontPanelBase__stop_acquisition__raises_error_if_spi_already_stopped():
    fp = FrontPanelBase()
    fp.initialize_board()
    assert fp.is_spi_running() is False
    with pytest.raises(OpalKellySpiAlreadyStoppedError):
        fp.stop_acquisition()


def test_FrontPanelBase__stop_acquisition__sets_internal_spi_running_state():
    fp = FrontPanelBase()
    fp.initialize_board()
    fp.start_acquisition()
    assert fp.is_spi_running() is True
    fp.stop_acquisition()
    assert fp.is_spi_running() is False


# FrontPanel tests
def test_FrontPanel__initialize_board__calls_to_init_function(mocker):
    dummy_xem = okCFrontPanel()
    mocked_init = mocker.patch.object(front_panel, "initialize_board", autospec=True)
    fp = FrontPanel(dummy_xem)
    fp.initialize_board()
    mocked_init.assert_called_once_with(dummy_xem, bit_file_name=None)


def test_FrontPanel__initialize_board__passes_bit_file_name_to_init_function(
    mocker, test_bit_file_paths
):
    expected_bit_file_name = test_bit_file_paths[0]
    dummy_xem = okCFrontPanel()
    mocked_init = mocker.patch.object(front_panel, "initialize_board", autospec=True)
    fp = FrontPanel(dummy_xem)
    fp.initialize_board(bit_file_name=expected_bit_file_name)
    mocked_init.assert_called_once_with(dummy_xem, bit_file_name=expected_bit_file_name)


def test_FrontPanel__initialize_board__allow_board_reinitialization_kwarg_suppresses_error(
    mocker, test_bit_file_paths
):
    dummy_xem = okCFrontPanel()
    mocked_init = mocker.patch.object(front_panel, "initialize_board", autospec=True)
    fp = FrontPanel(dummy_xem)

    fp.initialize_board(bit_file_name=test_bit_file_paths[0])
    assert fp.get_bit_file_name() == test_bit_file_paths[0]
    assert fp.is_board_initialized() is True
    fp.initialize_board(
        bit_file_name=test_bit_file_paths[1], allow_board_reinitialization=True
    )
    assert fp.get_bit_file_name() == test_bit_file_paths[1]

    mocked_init.assert_has_calls(
        [
            mocker.call(dummy_xem, bit_file_name=test_bit_file_paths[0]),
            mocker.call(dummy_xem, bit_file_name=test_bit_file_paths[1]),
        ]
    )


def test_FrontPanel__read_wire_out__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_wire_out(1)


def test_FrontPanel__read_wire_out__reads_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = 12
    mocked_read = mocker.patch.object(
        front_panel, "read_wire_out", autospec=True, return_value=expected
    )
    actual = fp.read_wire_out(3)
    assert actual == expected
    mocked_read.assert_called_once_with(dummy_xem, 3)


def test_FrontPanel__set_device_id__raises_error_if_id_is_too_many_bytes(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    mocker.patch.object(front_panel, "set_device_id", autospec=True)
    new_id = "123456789012345678901234567890123"
    with pytest.raises(OpalKellyIDGreaterThan32BytesError):
        fp.set_device_id(new_id)


def test_FrontPanel__set_device_id__passes_id_to_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    mocked_set = mocker.patch.object(front_panel, "set_device_id", autospec=True)
    fp.set_device_id("")
    mocked_set.assert_called_once_with(dummy_xem, "")


def test_FrontPanel__get_device_id__reads_id_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = "Mantarray XEM"
    mocked_get = mocker.patch.object(
        front_panel, "get_device_id", autospec=True, return_value=expected
    )
    actual = fp.get_device_id()
    assert actual == expected
    mocked_get.assert_called_once_with(dummy_xem)


def test_FrontPanel__read_from_fifo__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_from_fifo()


def test_FrontPanel__read_from_fifo__reads_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN)
    mocked_read = mocker.patch.object(
        front_panel, "read_from_fifo", autospec=True, return_value=expected
    )
    actual = fp.read_from_fifo()
    assert actual == expected
    mocked_read.assert_called_once_with(dummy_xem)


def test_FrontPanel__get_num_words_fifo__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.get_num_words_fifo()


def test_FrontPanel__get_num_words_fifo__gets_num_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = DATA_FRAME_SIZE_WORDS
    mocked_get = mocker.patch.object(
        front_panel, "get_num_words_fifo", autospec=True, return_value=expected
    )
    actual = fp.get_num_words_fifo()
    assert actual == expected
    mocked_get.assert_called_once_with(dummy_xem)


def test_FrontPanel__is_spi_running__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.is_spi_running()


def test_FrontPanel__is_spi_running__gets_status_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = False
    mocked_spi = mocker.patch.object(
        front_panel, "is_spi_running", autospec=True, return_value=expected
    )
    actual = fp.is_spi_running()
    assert actual == expected
    mocked_spi.assert_called_once_with(dummy_xem)


def test_FrontPanel__start_acquisition__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.start_acquisition()


def test_FrontPanel__start_acquisition__raises_error_if_spi_already_started(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    mocker.patch.object(front_panel, "is_spi_running", autospec=True, return_value=True)
    with pytest.raises(OpalKellySpiAlreadyStartedError):
        fp.start_acquisition()


def test_FrontPanel__start_acquisition__starts_running_spi_on_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    mocker.patch.object(
        front_panel, "is_spi_running", autospec=True, return_value=False
    )
    mocked_start = mocker.patch.object(front_panel, "start_acquisition", autospec=True)
    fp.start_acquisition()
    mocked_start.assert_called_once_with(dummy_xem)


def test_FrontPanel__stop_acquisition__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.stop_acquisition()


def test_FrontPanel__stop_acquisition__raises_error_if_spi_already_stopped(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    mocker.patch.object(
        front_panel, "is_spi_running", autospec=True, return_value=False
    )
    with pytest.raises(OpalKellySpiAlreadyStoppedError):
        fp.stop_acquisition()


def test_FrontPanel__stop_acquisition__stops_running_spi_on_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    mocker.patch.object(front_panel, "is_spi_running", autospec=True, return_value=True)
    mocked_stop = mocker.patch.object(front_panel, "stop_acquisition", autospec=True)
    fp.stop_acquisition()
    mocked_stop.assert_called_once_with(dummy_xem)


def test_FrontPanel__get_serial_number__reads_serial_from_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    expected = FrontPanelBase.default_xem_serial_number
    mocked_get = mocker.patch.object(
        front_panel, "get_serial_number", autospec=True, return_value=expected
    )
    actual = fp.get_serial_number()
    assert actual == expected
    mocked_get.assert_called_once_with(dummy_xem)


def test_FrontPanel__set_wire_in__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.set_wire_in(0x00, 0x00000001, 0x00000001)


def test_FrontPanel__set_wire_in__sets_wire_on_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    mocked_set = mocker.patch.object(front_panel, "set_wire_in", autospec=True)
    fp.set_wire_in(0x00, 0x00000001, 0x00000001)
    mocked_set.assert_called_once_with(dummy_xem, 0x00, 0x00000001, 0x00000001)


def test_FrontPanel__activate_trigger_in__raises_error_if_board_not_initialized():
    dummy_xem = okCFrontPanel()
    fp = FrontPanel(dummy_xem)
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.activate_trigger_in(0x01, 0x01)


def test_FrontPanel__activate_trigger_in__activates_trig_on_xem(
    mocker, initialized_front_panel_with_dummy_xem
):
    fp = initialized_front_panel_with_dummy_xem
    dummy_xem = fp.get_xem()
    mocked_set = mocker.patch.object(front_panel, "activate_trigger_in", autospec=True)
    fp.activate_trigger_in(0x01, 0x01)
    mocked_set.assert_called_once_with(dummy_xem, 0x01, 0x01)


# FrontPanelSimulator tests
def test_FrontPanelSimulator__init__raises_error_if_fifo_populated_with_invalid_data_read():
    fifo = SimpleMultiprocessingQueue()
    fifo.put(bytearray(1))
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    with pytest.raises(FPSimulatorInvalidFIFOValueError):
        FrontPanelSimulator(queues)


def test_FrontPanelSimulator__init__raises_fifo_error_with_correct_message():
    fifo = SimpleMultiprocessingQueue()
    test_reads = [
        bytearray(0),
        bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN),
        bytearray(1),
    ]
    for data_read in test_reads:
        fifo.put(data_read)
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    with pytest.raises(
        FPSimulatorInvalidFIFOValueError, match="Invalid value at index 2"
    ):
        FrontPanelSimulator(queues)


def test_FrontPanelSimulator__read_wire_out__raises_error_if_board_not_initialized():
    fp = FrontPanelSimulator({})
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_wire_out(1)


def test_FrontPanelSimulator__read_wire_out__reads_two_values_from_queue():
    a_queue = SimpleMultiprocessingQueue()
    expected_1 = 55
    expected_2 = 22
    a_queue.put(expected_1)
    a_queue.put(expected_2)
    queues = {"wire_outs": {5: a_queue}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()
    actual_1 = fp.read_wire_out(5)
    actual_2 = fp.read_wire_out(5)
    assert actual_1 == expected_1
    assert actual_2 == expected_2


def test_FrontPanelSimulator__read_wire_out__reads_values_from_correct_address():
    queue_1 = SimpleMultiprocessingQueue()
    queue_2 = SimpleMultiprocessingQueue()
    expected_1 = 33
    expected_2 = 35
    queue_1.put(expected_1)
    queue_2.put(expected_2)
    queues = {"wire_outs": {6: queue_1, 8: queue_2}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()
    actual_1 = fp.read_wire_out(6)
    actual_2 = fp.read_wire_out(8)
    assert actual_1 == expected_1
    assert actual_2 == expected_2


def test_FrontPanelSimulator__set_device_id__sets_internal_id_string():
    new_id = "Mantarray XEM"
    fp = FrontPanelSimulator({})
    fp.set_device_id(new_id)
    assert fp.get_device_id() == new_id


def test_FrontPanelSimulator__set_device_id__raises_error_if_id_is_too_many_bytes():
    new_id = "123456789012345678901234567890123"
    fp = FrontPanelSimulator({})
    with pytest.raises(OpalKellyIDGreaterThan32BytesError):
        fp.set_device_id(new_id)


def test_FrontPanelSimulator__get_serial_number__returns_default_internal_xem_id():
    expected_serial_number = FrontPanelBase.default_xem_serial_number
    fp = FrontPanelSimulator({})
    assert fp.get_serial_number() == expected_serial_number


def test_FrontPanelSimulator__read_from_fifo__raises_error_if_board_not_initialized():
    fp = FrontPanelSimulator({})
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.read_from_fifo()


def test_FrontPanelSimulator__read_from_fifo__returns_correct_bytearray():
    expected = bytearray(
        [
            i % 256
            for i in range(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN)
        ]
    )
    fifo = SimpleMultiprocessingQueue()
    fifo.put(expected)
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()
    actual = fp.read_from_fifo()
    assert actual == expected


def test_FrontPanelSimulator__read_from_fifo__returns_two_bytearrays_in_correct_order():
    expected_1 = bytearray(0)
    expected_2 = bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN)
    fifo = SimpleMultiprocessingQueue()
    fifo.put(expected_1)
    fifo.put(expected_2)
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()
    actual_1 = fp.read_from_fifo()
    actual_2 = fp.read_from_fifo()
    assert actual_1 == expected_1
    assert actual_2 == expected_2


def test_FrontPanelSimulator__read_from_fifo__returns_two_bytearrays_in_correct_order__when_using_multiprocessing_queue():
    expected_1 = bytearray(0)
    expected_2 = bytearray(DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN)
    fifo = multiprocessing.Queue()
    fifo.put(expected_1)
    fifo.put(expected_2)
    assert is_queue_eventually_not_empty(fifo) is True
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()
    actual_1 = fp.read_from_fifo()
    assert is_queue_eventually_not_empty(fifo) is True
    actual_2 = fp.read_from_fifo()
    assert is_queue_eventually_empty(fifo) is True
    assert actual_1 == expected_1
    assert actual_2 == expected_2


def test_FrontPanelSimulator__get_num_words_fifo__raises_error_if_board_not_initialized():
    fp = FrontPanelSimulator({})
    with pytest.raises(OpalKellyBoardNotInitializedError):
        fp.get_num_words_fifo()


def test_FrontPanelSimulator__get_num_words_fifo__correctly_returns_num_words_of_2_reads():
    expected_num_words_1 = DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN
    expected_num_words_2 = DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN * 2
    test_bytearray_1 = bytearray(expected_num_words_1 * 4)
    test_bytearray_2 = bytearray(expected_num_words_2 * 4)
    fifo = SimpleMultiprocessingQueue()
    fifo.put(test_bytearray_1)
    fifo.put(test_bytearray_2)
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()

    actual_1 = fp.get_num_words_fifo()
    assert actual_1 == expected_num_words_1
    fp.read_from_fifo()
    actual_2 = fp.get_num_words_fifo()
    assert actual_2 == expected_num_words_2


def test_FrontPanelSimulator__get_num_words_fifo__correctly_returns_num_words_of_2_reads__when_using_multiprocessing_queue():
    expected_num_words_1 = DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN
    expected_num_words_2 = DATA_FRAME_SIZE_WORDS * DATA_FRAMES_PER_ROUND_ROBIN * 2
    test_bytearray_1 = bytearray(expected_num_words_1 * 4)
    test_bytearray_2 = bytearray(expected_num_words_2 * 4)
    fifo = multiprocessing.Queue()
    fifo.put(test_bytearray_1)
    fifo.put(test_bytearray_2)
    assert is_queue_eventually_not_empty(fifo) is True
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()

    actual_1 = fp.get_num_words_fifo()
    assert actual_1 == expected_num_words_1
    fp.read_from_fifo()
    actual_2 = fp.get_num_words_fifo()
    assert actual_2 == expected_num_words_2


def test_FrontPanelSimulator__get_num_words_fifo__returns_0_when_fifo_queue_is_empty():
    expected_num_words = 0
    fifo = multiprocessing.Queue()
    queues = {"pipe_outs": {PIPE_OUT_FIFO: fifo}}
    fp = FrontPanelSimulator(queues)
    fp.initialize_board()

    actual = fp.get_num_words_fifo()
    assert actual == expected_num_words
