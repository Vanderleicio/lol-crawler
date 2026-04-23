from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self):
        """Método para extrair os dados dos sites usados."""
        pass