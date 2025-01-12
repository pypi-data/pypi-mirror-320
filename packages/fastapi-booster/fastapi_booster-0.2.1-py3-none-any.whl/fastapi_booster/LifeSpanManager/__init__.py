import asyncio
import logging
from contextlib import asynccontextmanager
from math import inf
from typing import Callable, List

from Akatosh.universe import Mundus
from fastapi import FastAPI



class LifeSpanManager:
    """Singleton class to manage the lifespan of a FastAPI application.

    This class ensures that startup and shutdown functions are executed
    when the application starts and stops, respectively.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create a new instance of LifeSpanManager if it doesn't exist.

        Returns:
            LifeSpanManager: The single instance of the LifeSpanManager class.
        """
        if not cls._instance:
            cls._instance = super(LifeSpanManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the LifeSpanManager with empty startup and shutdown function lists."""
        self._start_up_functions: List[Callable] = []
        self._shutdown_functions: List[Callable] = []


lifespan_manager = LifeSpanManager()


def startup_function(function: Callable):
    """Register a function to be called at application startup.

    Args:
        function (Callable): The function to be called at startup.
    """
    lifespan_manager._start_up_functions.append(function)


def shutdown_function(function: Callable):
    """Register a function to be called at application shutdown.

    Args:
        function (Callable): The function to be called at shutdown.
    """
    lifespan_manager._shutdown_functions.append(function)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager to handle the lifespan of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    Mundus.enable_realtime()
    Mundus.set_logging_level(logging.INFO)
    asyncio.create_task(Mundus.simulate(till=inf))
    for function in lifespan_manager._start_up_functions:
        if asyncio.iscoroutinefunction(function):
            await function()
        else:
            function()
    lifespan_manager._start_up_functions.clear()
    yield
    for function in lifespan_manager._shutdown_functions:
        if asyncio.iscoroutinefunction(function):
            await function()
        else:
            function()
    lifespan_manager._shutdown_functions.clear()
