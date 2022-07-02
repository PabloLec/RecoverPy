from threading import Lock
from typing import Any, Dict


class SingletonMeta(type):
    """Thread-safe implementation of Singleton."""

    _instances: Dict[Any, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
