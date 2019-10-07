class AppException(Exception):
    code = str(None)

    def __init__(self, value):
        AppException.__init__(self, value, None)

    def __init__(self, value, code):
        self.value = value
        self.code = code

    def __str__(self):
        return repr(self.value)