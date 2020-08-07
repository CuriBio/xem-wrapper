# -*- coding: utf-8 -*-
import os

import pytest
from stdlib_utils import get_current_file_abs_directory
from xem_wrapper import front_panel
from xem_wrapper import FrontPanel
from xem_wrapper import okCFrontPanel


@pytest.fixture(scope="function", name="initialized_front_panel_with_dummy_xem")
def fixture_initialized_front_panel_with_dummy_xem(mocker):
    dummy_xem = okCFrontPanel()
    mocker.patch.object(front_panel, "initialize_board", autospec=True)
    fp = FrontPanel(dummy_xem)
    fp.initialize_board()
    yield fp


@pytest.fixture(scope="function", name="test_bit_file_paths")
def fixture_test_bit_file_paths():
    base_path = os.path.join(get_current_file_abs_directory(), "test_bit_files")
    test_path_0 = os.path.join(base_path, "test_file_0.bit")
    test_path_1 = os.path.join(base_path, "test_file_1.bit")

    yield test_path_0, test_path_1
