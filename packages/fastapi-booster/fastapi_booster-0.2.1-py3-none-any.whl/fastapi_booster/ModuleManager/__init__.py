from __future__ import annotations

from fastapi_booster.LifeSpanManager import startup_function, shutdown_function
from fastapi_booster import logger
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_booster.Module import Module


class ModuleManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModuleManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.modules: Dict[str, Module] = {}

        @startup_function
        def module_db_init():
            for module in self.modules.values():
                logger.info(f"Module {module.name}:\tinitializing...")
                module.update_all_tables_schema()
                logger.info(f"Module {module.name}:\tinitialized")
    

    
