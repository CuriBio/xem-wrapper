# -*- coding: utf-8 -*-
"""Global constants related to the OpalKelly board configuration."""
# USB transfer related values
HEADER_MAGIC_NUMBER = 0xC691199927021942
BLOCK_SIZE = 32  # must be a power of 2, ideally equal to size of data frame
DATA_FRAME_SIZE_WORDS = 9
DATA_FRAMES_PER_ROUND_ROBIN = 8

# Trigger-in values
TRIGGER_IN_SPI = 0x41

# Wire-in values
WIRE_IN_RESET_MODE = 0x00
WIRE_IN_NUM_SAMPLES = 0x01

# Wire-out values
WIRE_OUT_NUM_WORDS_FIFO = 0x20
WIRE_OUT_IS_SPI_RUNNING = 0x22
WIRE_OUT_IS_PLL_LOCKED = 0x24  # Not used in mantarray

# Pipe-out values
PIPE_OUT_FIFO = 0xA0
