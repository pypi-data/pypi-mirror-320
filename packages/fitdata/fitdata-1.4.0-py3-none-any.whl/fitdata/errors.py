class InvalidGlobalDataException(Exception):
    """
    Exception raised when the provided global data is invalid or inconsistent.

    This exception is typically used to handle errors in user input,
    such as when the current weight and target weight are incompatible
    with the specified objective.
    """

    def __init__(self, *args):
        super().__init__(*args)
