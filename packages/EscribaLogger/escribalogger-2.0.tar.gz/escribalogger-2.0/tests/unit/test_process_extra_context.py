import re

from EscribaLogger.process_extra_context import process_extra_context


def test_should_process_extra_context():
    sample_dict = {"key": "value"}
    result = process_extra_context(sample_dict)
    assert result == ' - {"key": "value"}'


def test_should_return_empty_string_when_empty_context():
    result = process_extra_context({})
    assert result == ""


def test_should_return_empty_string_when_context_is_none():
    result = process_extra_context(None)
    assert result == ""


def test_should_convert_object_instances_to_string():
    class Item:
        param = "Escriba param"

        def __init__(self) -> None:
            self.name = "the Escriba"

        def __str__(self):
            return "the Escriba"

    sample_dict = {"full_class": Item, "object": Item()}
    result = process_extra_context(sample_dict)

    assert type(result) is str
    assert re.search(r"\.Item", result)
    assert re.search(r"<object \(Item\)\>: the Escriba", result)
    assert re.search(r"\.Item", result)
    assert re.search(r"<object \(Item\)\>: the Escriba", result)
