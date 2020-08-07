# -*- coding: utf-8 -*-
from xem_wrapper import BLOCK_SIZE
from xem_wrapper import DATA_FRAME_SIZE_WORDS
from xem_wrapper import DATA_FRAMES_PER_ROUND_ROBIN
from xem_wrapper import HEADER_MAGIC_NUMBER
from xem_wrapper import PIPE_OUT_FIFO
from xem_wrapper import TRIGGER_IN_SPI
from xem_wrapper import WIRE_IN_NUM_SAMPLES
from xem_wrapper import WIRE_IN_RESET_MODE
from xem_wrapper import WIRE_OUT_IS_PLL_LOCKED
from xem_wrapper import WIRE_OUT_IS_SPI_RUNNING
from xem_wrapper import WIRE_OUT_NUM_WORDS_FIFO


def test_usb_transfer_values():
    assert HEADER_MAGIC_NUMBER == 0xC691199927021942
    assert BLOCK_SIZE == 32
    assert DATA_FRAME_SIZE_WORDS == 9
    assert DATA_FRAMES_PER_ROUND_ROBIN == 8


def test_endpoints():
    assert WIRE_IN_RESET_MODE == 0x00
    assert WIRE_IN_NUM_SAMPLES == 0x01

    assert WIRE_OUT_NUM_WORDS_FIFO == 0x20
    assert WIRE_OUT_IS_SPI_RUNNING == 0x22
    assert WIRE_OUT_IS_PLL_LOCKED == 0x24

    assert TRIGGER_IN_SPI == 0x41

    assert PIPE_OUT_FIFO == 0xA0
