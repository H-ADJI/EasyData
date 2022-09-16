'''
File: browser_errors.py
File Created: Monday, 18th July 2022 10:39:57 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''


class BrowserException(Exception):
    """Parent class for all browser related errors
    """

    def __init__(self, message: str = "Error: There is something wrong in your browser") -> None:
        super().__init__(message)


class BrowserActionException(BrowserException):
    """Parent class for all browser actions related errors
    """
    pass


class ActionsFallback(BrowserActionException):
    pass


class ClickButtonError(BrowserActionException):
    pass


class TypingTextError(BrowserActionException):
    pass


class UseKeyboardError(BrowserActionException):
    pass


class UploadFileError(BrowserActionException):
    def __init__(self, message: str = "Error: CAN'T UPLOAD THE FILES PROVIDED") -> None:
        super().__init__(message)


class HoverOverError(BrowserActionException):
    pass


class WaitingError(BrowserActionException):
    def __init__(self, message: str = "Could not wait for elements provided") -> None:
        super().__init__(message)


class AttributeRetrievalError(BrowserActionException):
    def __init__(self, message: str = "Could not retrieve attribute") -> None:
        super().__init__(message)


class TextRetrievalError(BrowserActionException):
    def __init__(self, message: str = "Could not retrieve text") -> None:
        super().__init__(message)
