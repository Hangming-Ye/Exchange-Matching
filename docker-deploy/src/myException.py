class ArgumentError(RuntimeError):
    msg  = ""
    def __init__(self, msg):
        self.msg = msg