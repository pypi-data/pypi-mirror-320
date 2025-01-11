from typing import List, Union
import numpy as np
import openai
from .base import BaseEmbedding

class OpenAIEmbedding(BaseEmbedding):
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        batch_size: int = 100
    ):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size
        self._dimension = self._get_model_dimension()
        
    def _get_model_dimension(self) -> int:
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions.get(self.model, 1536)
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
            
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            batch_embeddings = [e.embedding for e in response.data]
            all_embeddings.extend(batch_embeddings)
            
        return np.array(all_embeddings)
    
    def get_dimension(self) -> int:
        return self._dimension
