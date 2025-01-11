from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np

class BaseEmbedding(ABC):
    @abstractmethod
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for input texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding dimension."""
        pass
