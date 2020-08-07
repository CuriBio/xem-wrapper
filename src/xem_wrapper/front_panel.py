# -*- coding: utf-8 -*-
"""Class-based interfaces for interacting with a XEM."""
from __future__ import annotations

from collections import deque
import multiprocessing
from typing import Any
from typing import Callable
from typing import cast
from typing import Deque
from typing import Dict
from typing import Optional
from typing import TypeVar
from typing import Union

from stdlib_utils import is_queue_eventually_not_empty
from stdlib_utils import SimpleMultiprocessingQueue

from .constants import DATA_FRAME_SIZE_WORDS
from .constants import DATA_FRAMES_PER_ROUND_ROBIN
from .constants import PIPE_OUT_FIFO
from .exceptions import FPSimulatorInvalidFIFOValueError
from .exceptions import OpalKellyBoardAlreadyInitializedError
from .exceptions import OpalKellyBoardNotInitializedError
from .exceptions import OpalKellySpiAlreadyStartedError
from .exceptions import OpalKellySpiAlreadyStoppedError
from .main import activate_trigger_in
from .main import check_file_exists
from .main import get_device_id
from .main import get_num_words_fifo
from .main import get_serial_number
from .main import initialize_board
from .main import is_spi_running
from .main import read_from_fifo
from .main import read_wire_out
from .main import set_device_id
from .main import set_wire_in
from .main import start_acquisition
from .main import stop_acquisition
from .main import validate_device_id
from .ok import okCFrontPanel

GenericFunctionType = TypeVar(
    "GenericFunctionType", bound=Callable[..., Any]
)  # https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators


def validate_simulated_fifo_reads(
    fifo: Union[
        SimpleMultiprocessingQueue,
        multiprocessing.queues.Queue[  # pylint: disable=unsubscriptable-object # https://github.com/PyCQA/pylint/issues/1498
            bytearray
        ],
    ]
) -> None:
    """Validate that all bytearrays in the FIFO will be of appropriate size.

    Args:
        fifo: SimpleMultiprocessingQueue or multiprocessing.Queue containing bytearrays
    """
    if not is_queue_eventually_not_empty(fifo):
        return

    temp_fifo: Deque[bytearray] = deque()
    idx = 0
    while is_queue_eventually_not_empty(fifo):
        fifo_read = fifo.get_nowait()
        if (
            len(fifo_read) % (DATA_FRAME_SIZE_WORDS * 4 * DATA_FRAMES_PER_ROUND_ROBIN)
            != 0
        ):
            raise FPSimulatorInvalidFIFOValueError(f"Invalid value at index {idx}")
        temp_fifo.append(fifo_read)
        idx += 1
    for _ in range(idx):
        fifo.put(temp_fifo.popleft())

    is_fifo_populated = False
    while not is_fifo_populated:
        is_fifo_populated = is_queue_eventually_not_empty(fifo)


def board_must_be_initialized(
    method_to_decorate: GenericFunctionType,
) -> GenericFunctionType:  # noqa: D202 # Black automatically puts a blank line between the docstring and the decorator definition
    """Confirm board is initialized.

    Based on https://stackoverflow.com/questions/38286098/python-method-decorator-to-access-an-instance-variable/38286176

    To be used as a decorator for methods that logically require the board to be initialized before they should ever be run.
    """

    def decorator(
        self: Any, *args: Any, **kwargs: Any
    ) -> Any:  # Eli (3/10/20) not sure how to declare the 'self' as type FrontPanelBase...positioning the decorator definition above the class definition gives errors in the decorator, and below the class definition gives errors in the class...
        if not self.is_board_initialized():
            raise OpalKellyBoardNotInitializedError()
        return method_to_decorate(self, *args, **kwargs)

    return cast(GenericFunctionType, decorator)


class FrontPanelBase:
    """Base class that performs actions relevant to live board and simulation.

    Such as error checking the order of commands etc.
    """

    default_xem_serial_number = "1917000Q70"

    def __init__(self) -> None:
        self._is_board_initialized = False
        self._bit_file_name: Optional[str] = None
        self._device_id = ""
        self._is_spi_running = False
        self._serial_number = self.default_xem_serial_number

    def is_board_initialized(self) -> bool:
        return self._is_board_initialized

    def initialize_board(
        self,
        bit_file_name: Optional[str] = None,
        allow_board_reinitialization: bool = False,
    ) -> None:
        """Initialize FrontPanel."""
        # pylint: disable=unused-argument # this is needed so that the function signatures match for subclasses that override it. maybe later there might be error checking that the file is actually a .bit file...
        if self.is_board_initialized() and not allow_board_reinitialization:
            raise OpalKellyBoardAlreadyInitializedError()
        if bit_file_name is not None:
            check_file_exists(bit_file_name)

        self._is_board_initialized = True
        self._bit_file_name = bit_file_name

    @board_must_be_initialized
    def read_wire_out(self, ep_addr: int) -> int:
        # pylint: disable=unused-argument # this is needed so that the function signatures match for subclasses that override it
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        return 0

    @board_must_be_initialized
    def set_wire_in(self, ep_addr: int, value: int, mask: int) -> None:
        # pylint: disable=unused-argument # this is needed so that the function signatures match for subclasses that override it
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        return

    def set_device_id(self, new_id: str) -> None:
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        validate_device_id(new_id)

    @board_must_be_initialized
    def read_from_fifo(self) -> bytearray:
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        return bytearray(0)

    @board_must_be_initialized
    def get_num_words_fifo(self) -> int:
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        return 0

    def get_serial_number(self) -> str:
        return self._serial_number

    def get_device_id(self) -> str:
        return self._device_id

    def get_bit_file_name(self) -> Optional[str]:
        return self._bit_file_name

    def get_internal_spi_running_status(self) -> bool:
        return self._is_spi_running

    @board_must_be_initialized
    def is_spi_running(self) -> bool:
        return self._is_spi_running

    @board_must_be_initialized
    def start_acquisition(self) -> None:
        if self.is_spi_running():
            raise OpalKellySpiAlreadyStartedError()
        self._is_spi_running = True

    @board_must_be_initialized
    def stop_acquisition(self) -> None:
        if not self.is_spi_running():
            raise OpalKellySpiAlreadyStoppedError()
        self._is_spi_running = False

    @board_must_be_initialized
    def activate_trigger_in(self, ep_addr: int, bit: int) -> None:
        # pylint: disable=unused-argument # this is needed so that the function signatures match for subclasses that override it
        # pylint: disable=no-self-use # this is needed so that the function signatures match for subclasses that override it
        return


class FrontPanel(FrontPanelBase):
    """Class-based interface for interacting with a XEM."""

    def __init__(self, xem: okCFrontPanel):
        super().__init__()
        self._xem = xem

    def get_xem(self) -> okCFrontPanel:
        return self._xem

    def initialize_board(
        self,
        bit_file_name: Optional[str] = None,
        allow_board_reinitialization: bool = False,
    ) -> None:
        super().initialize_board(
            bit_file_name=bit_file_name,
            allow_board_reinitialization=allow_board_reinitialization,
        )
        initialize_board(self.get_xem(), bit_file_name=bit_file_name)

    def read_wire_out(self, ep_addr: int) -> int:
        super().read_wire_out(ep_addr)
        return read_wire_out(self.get_xem(), ep_addr)

    def set_wire_in(self, ep_addr: int, value: int, mask: int) -> None:
        super().set_wire_in(ep_addr, value, mask)
        set_wire_in(self.get_xem(), ep_addr, value, mask)

    def set_device_id(self, new_id: str) -> None:
        super().set_device_id(new_id)
        set_device_id(self.get_xem(), new_id)

    def get_device_id(self) -> str:
        return get_device_id(self.get_xem())

    def get_serial_number(self) -> str:
        return get_serial_number(self.get_xem())

    def get_num_words_fifo(self) -> int:
        super().get_num_words_fifo()
        return get_num_words_fifo(self.get_xem())

    def read_from_fifo(self) -> bytearray:
        super().read_from_fifo()
        return read_from_fifo(self.get_xem())

    def is_spi_running(self) -> bool:
        super().is_spi_running()
        return is_spi_running(self.get_xem())

    def start_acquisition(self) -> None:
        super().start_acquisition()
        start_acquisition(self.get_xem())

    def stop_acquisition(self) -> None:
        super().stop_acquisition()
        stop_acquisition(self.get_xem())

    def activate_trigger_in(self, ep_addr: int, bit: int) -> None:
        super().activate_trigger_in(ep_addr, bit)
        activate_trigger_in(self.get_xem(), ep_addr, bit)


class FrontPanelSimulator(FrontPanelBase):
    """Simulates a okCFrontPanel/XEM object.

    Args:
        simulated_response_queues: dictionary where the ultimate leaves should be multiprocessing_utils.SimpleMultiprocessingQueue or multiprocessing.Queue objects. These values are popped off the end of the queue and returned as if coming from the XEM. The 'wire_outs' key should contain a sub-dict with keys of integer values representing the ep addresses.
    """

    def __init__(self, simulated_response_queues: Dict[str, Any]):
        super().__init__()
        if "pipe_outs" in simulated_response_queues:
            pipe_outs = simulated_response_queues["pipe_outs"]
            fifo = pipe_outs[PIPE_OUT_FIFO]
            validate_simulated_fifo_reads(fifo)
        self._simulated_response_queues = simulated_response_queues
        self._is_spi_running = False

    def read_wire_out(self, ep_addr: int) -> int:
        super().read_wire_out(ep_addr)
        wire_out_queues = self._simulated_response_queues["wire_outs"]
        the_queue = wire_out_queues[ep_addr]
        simulated_wire_out_value = the_queue.get_nowait()
        if not isinstance(simulated_wire_out_value, int):
            raise NotImplementedError(
                "Items put into the simulated wire outs must always be of type int."
            )

        return simulated_wire_out_value

    def set_device_id(self, new_id: str) -> None:
        super().set_device_id(new_id)
        self._device_id = new_id

    def read_from_fifo(self) -> bytearray:
        super().read_from_fifo()
        pipe_out_queues = self._simulated_response_queues["pipe_outs"]
        fifo = pipe_out_queues[PIPE_OUT_FIFO]
        this_fifo_bytearray = fifo.get_nowait()
        if not isinstance(this_fifo_bytearray, bytearray):
            raise NotImplementedError(
                "Items put into the simulated FIFO should always be of type bytearray."
            )
        return this_fifo_bytearray

    def get_num_words_fifo(self) -> int:
        super().get_num_words_fifo()
        pipe_out_queues = self._simulated_response_queues["pipe_outs"]
        fifo = pipe_out_queues[PIPE_OUT_FIFO]
        if not is_queue_eventually_not_empty(fifo):
            return 0

        temp_fifo: Deque[bytearray] = deque()
        num_words = 0
        idx = 0
        while is_queue_eventually_not_empty(fifo):
            fifo_read = fifo.get_nowait()
            if idx == 0:
                num_words = len(fifo_read) // 4
            temp_fifo.append(fifo_read)
            idx += 1
        for _ in range(idx):
            fifo.put(temp_fifo.popleft())

        is_fifo_populated = False
        while not is_fifo_populated:
            is_fifo_populated = is_queue_eventually_not_empty(fifo)

        return num_words
