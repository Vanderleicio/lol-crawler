from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def extrair_dados(self, url):
        """Método para extrair os dados dos sites usados."""
        pass