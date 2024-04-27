from dto.prototypes import ResponsePrototype


class SimpleResult(ResponsePrototype):
    def __init__(self, result: bool):
        self.result = result
