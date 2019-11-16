class AppException(Exception):
    code = str(None)
    value = str(None)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)