from modules.tui import TUI
from utils.enums import ReturnCode
import pytest

base_inputs = [("help", ReturnCode.SUCCESS), ("", ReturnCode.NO_INPUT)]
sync_inputs = [
    ("sync", ReturnCode.MISSING_ARGUMENT),
    ("sync test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
]

data_not_loaded_inputs = [
    ("data", ReturnCode.MISSING_ARGUMENT),
    ("data test_case_pytest", ReturnCode.NO_COMMAND),
    ("data new", ReturnCode.MISSING_ARGUMENT),
    ("data new test", ReturnCode.SUCCESS),
    ("data load", ReturnCode.MISSING_ARGUMENT),
    ("data load test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
    ("data load test", ReturnCode.SUCCESS),
    ("data expand", ReturnCode.MISSING_ARGUMENT),
    ("data expand spotify", ReturnCode.MISSING_ARGUMENT),
    ("data expand spotify test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
    ("data expand test_case_pytest spotify", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify spotify", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify youtube str", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify youtube", ReturnCode.NOT_LOADED),
    ("data expand spotify youtube 2", ReturnCode.NOT_LOADED),
    ("data guess", ReturnCode.NOT_LOADED),
    ("data process", ReturnCode.NOT_LOADED),
    ("data expand spotify youtube", ReturnCode.SUCCESS),
    ("data expand spotify youtube 2", ReturnCode.SUCCESS),
    ("data guess", ReturnCode.NOT_LOADED),
    ("data process true", ReturnCode.NOT_LOADED),
    ("data process", ReturnCode.NOT_LOADED),
]

data_loaded_inputs = [
    ("data", ReturnCode.MISSING_ARGUMENT),
    ("data test_case_pytest", ReturnCode.NO_COMMAND),
    ("data new", ReturnCode.MISSING_ARGUMENT),
    ("data new test", ReturnCode.SUCCESS),
    ("data load", ReturnCode.MISSING_ARGUMENT),
    ("data load test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
    ("data load test", ReturnCode.SUCCESS),
    ("data expand", ReturnCode.MISSING_ARGUMENT),
    ("data expand spotify", ReturnCode.MISSING_ARGUMENT),
    ("data expand spotify test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
    ("data expand test_case_pytest spotify", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify spotify", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify youtube str", ReturnCode.NO_VALIDE_INPUT),
    ("data expand spotify youtube", ReturnCode.SUCCESS),
    ("data expand spotify youtube 2", ReturnCode.SUCCESS),
    ("data guess", ReturnCode.SUCCESS),
    ("data process true", ReturnCode.SUCCESS),
    ("data process", ReturnCode.SUCCESS),
]

eval_inputs = [
    ("eval", ReturnCode.MISSING_ARGUMENT),
    ("eval test_case_pytest", ReturnCode.NO_VALIDE_INPUT),
    ("eval test", ReturnCode.SUCCESS),
]


@pytest.mark.parametrize("inputs, expected", base_inputs)
def test_base_inputs(inputs, expected):
    tui = TUI()
    tui.cur_input = inputs.split(" ")
    assert tui.match_user_input() == expected

@pytest.mark.parametrize("inputs, expected", sync_inputs)
def test_sync_inputs(inputs, expected):
    tui = TUI()
    tui.cur_input = inputs.split(" ")
    assert tui.match_user_input() == expected

@pytest.mark.parametrize("inputs, expected", data_not_loaded_inputs)
def test_data_not_loaded_inputs(inputs, expected):
    tui = TUI()
    tui.cur_input = inputs.split(" ")
    assert tui.match_user_input() == expected

@pytest.mark.parametrize("inputs, expected", data_loaded_inputs)
def test_data_loaded_inputs(inputs, expected):
    tui = TUI()
    tui.cur_input = ["data", "load", "test"]
    tui.match_user_input()

    tui.cur_input = inputs.split(" ")
    assert tui.match_user_input() == expected

@pytest.mark.parametrize("inputs, expected", eval_inputs)
def test_eval_inputs(inputs, expected):
    tui = TUI()
    tui.cur_input = inputs.split(" ")
    assert tui.match_user_input() == expected

def test_exit():
    tui = TUI()
    tui.cur_input = ["exit"]
    assert tui.match_user_input() == ReturnCode.SUCCESS
    assert not tui.running
