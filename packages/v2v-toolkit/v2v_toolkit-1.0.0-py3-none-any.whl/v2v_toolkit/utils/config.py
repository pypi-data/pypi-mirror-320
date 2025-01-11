import dataclasses
import logging


@dataclasses.dataclass
class ConfigBaseStruct:
    """Base parameters container struct to map config files to python objects."""

    logging_enabled: bool = False  # is logging enabled?
    logging_level: str = (
        "INFO"  # logging level from [DEBUG, INFO, WARNING, ERROR, CRITICAL]
    )
    caching: bool = False  # is caching enabled?
    max_cache_size: int = -1  # max cache size in bytes

    def __post_init__(self):
        """Set default values if not provided.

        Returns:
            None
        """
        if self.caching and self.max_cache_size == -1:
            self.max_cache_size = 1024 * 1024 * 1024
        if self.logging_enabled:
            self.logging_level = logging.getLevelName(self.logging_level)
