import logging

import pytest

from EscribaLogger.Log import Log


@pytest.fixture
def log_obj():
    return Log()


def test_log_should_be_a_singleton(log_obj: Log):
    assert log_obj == Log()


def test_log_can_change_name():
    default_logger_name = Log.log_name()
    new_logger_name = "my_logger_test"
    Log.set_logger_name(new_logger_name)
    assert Log.log_name() == new_logger_name and Log.log_name() != default_logger_name


def test_log_can_add_drivers():
    number_of_default_drivers = len(Log.root_logger.handlers)
    Log.add_driver("stdout")
    number_of_current_drivers = len(Log.root_logger.handlers)
    Log.clear_drivers()
    assert number_of_current_drivers == 1 and number_of_default_drivers == 0


def test_log_cannot_add_same_driver_twice():
    number_of_default_drivers = len(Log.root_logger.handlers)
    Log.add_driver("stdout")
    Log.add_driver("stdout")
    number_of_current_drivers = len(Log.root_logger.handlers)
    Log.clear_drivers()
    assert number_of_current_drivers == 1 and number_of_default_drivers == 0


def test_log_cannot_add_unexistent_driver():
    with pytest.raises(Exception):
        Log.add_driver("BadDriver")


def test_log_can_add_generic_driver():
    class CustomGenericHandler(logging.Handler):
        ...

    Log.add_driver(
        "newDriver", driver_func=lambda driver_option: CustomGenericHandler()
    )

    log_handlers = Log.root_logger.handlers
    assert (
        type(log_handlers[0]).__name__ == "CustomGenericHandler"
        and len(log_handlers) == 1
    )


def test_log_can_remove_generic_driver():
    class CustomGenericHandler(logging.Handler):
        ...

    Log.add_driver(
        "newDriver", driver_func=lambda driver_option: CustomGenericHandler()
    )

    Log.add_driver("file")
    Log.remove_driver("file")

    stream_type = Log.drivers["newDriver"](None)
    Log.remove_driver("newDriver")
    log_drivers = Log.drivers.keys()
    current_drivers = Log.root_logger.handlers
    assert len(current_drivers) == 0
