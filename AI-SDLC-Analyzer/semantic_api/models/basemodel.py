from abc import ABC, abstractmethod

class BaseSearchModel(ABC):
    @abstractmethod
    def encode(self, text):
        pass

    @abstractmethod
    def search(self, query, top_k=1):
        pass
