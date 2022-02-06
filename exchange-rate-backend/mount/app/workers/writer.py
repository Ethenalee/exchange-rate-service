from typing import List


def handler(*event_name):
    def wrapper(function):
        function.event_name = event_name
        return function

    return wrapper


class WriterOutput:
    def __init__(self):
        self.handlers = {}

        for method_name in dir(self):
            method = getattr(self, method_name)
            if (event_name := getattr(method, "event_name", None)) is not None:
                self.handlers[event_name] = method

    def write(self, event_name, *args, **kwargs):
        if event_name in self.handlers:
            self.handlers[event_name](*args, **kwargs)


class Writer:
    outputs: List[WriterOutput] = []

    @classmethod
    def register_output(cls, output: WriterOutput) -> None:
        cls.outputs.append(output)

    @classmethod
    def write(cls, event_name: tuple, *args, **kwargs) -> None:
        for output in cls.outputs:
            output.write(event_name, *args, **kwargs)
