class MenuError(Exception):
    """
    Custom exception for console related stuff since I dont want to catch too many exceptions
    from Python.
    """


class MenuQuit(Exception):
    """
    For exiting all console instances
    """
