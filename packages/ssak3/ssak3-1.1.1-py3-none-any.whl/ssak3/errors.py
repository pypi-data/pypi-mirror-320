CODE_OK = 0
CODE_1001 = 1001    # internal error
CODE_2001 = 2001    # llm error
CODE_3001 = 3001    # llm warning

# --------------------------------------------------------------------------------------------------------------
class ClzError(Exception):
    def __init__(self, message="CLZ Error", code=CODE_1001):
        self.message = message
        self.code = code
        self.fmt = self._format_message()
        super().__init__(self.fmt)

    def _format_message(self):
        # ( 2001) CLZ Internal Error
        return f'({self.code:5d}) {self.message}'

    def __str__(self):
        return self.fmt
    
# --------------------------------------------------------------------------------------------------------------
class ClzInternalError(ClzError):
    def __init__(self, message='CLZ Internal Error', code=CODE_2001, input_value=None):
        self.input_value = input_value
        super().__init__(message, code)
        if input_value:
            self.fmt = f'{self.fmt} | {input_value}'

    def __str__(self):
        return self.fmt

# eof
