class V2VError(Exception):
    """Base class for V2V Toolkit exceptions"""

    pass


class V2VGraphError(V2VError):
    """Exception raised when graph runtime fails"""

    pass


class V2VModuleError(V2VError):
    """Exception raised when node runtime fails"""

    pass
