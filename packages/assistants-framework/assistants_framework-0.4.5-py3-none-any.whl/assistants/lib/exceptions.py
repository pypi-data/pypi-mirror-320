class ConfigError(ValueError):
    """
    Exception for configuration errors.
    """
    pass

class NoResponseError(ValueError):
    """
    Exception for when there is no response from the assistant.
    """
    pass
