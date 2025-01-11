from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from .base import BaseEmbedding

class SentenceTransformerEmbedding(BaseEmbedding):
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32
    ):
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings
    
    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
