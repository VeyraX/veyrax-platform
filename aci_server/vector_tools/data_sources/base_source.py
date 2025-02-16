from abc import ABC, abstractmethod
from typing import Generator, Dict, Any

class BaseDataSource(ABC):
    """Abstract base class for all data sources"""
    
    @abstractmethod
    def get_documents(self) -> Generator[Dict[str, Any], None, None]:
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        pass