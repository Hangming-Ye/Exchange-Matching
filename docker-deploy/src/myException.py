class ArgumentError(RuntimeError):
    def __init__(self, arg):
        self.args = arg