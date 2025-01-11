from typing import Union, List, Optional
import numpy as np
from .models.base import BaseEmbedding
from .preprocessing.text_processor import TextProcessor

class TextEmbedder:
    def __init__(
        self,
        model: BaseEmbedding,
        preprocessor: Optional[TextProcessor] = None,
        cache_embeddings: bool = False
    ):
        self.model = model
        self.preprocessor = preprocessor or TextProcessor()
        self.cache_embeddings = cache_embeddings
        self._cache = {}
    
    def embed(
        self,
        texts: Union[str, List[str]],
        preprocess: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
            
        if preprocess:
            texts = [self.preprocessor.process(text) for text in texts]
            
        if self.cache_embeddings:
            cached_embeddings = []
            texts_to_embed = []
            indices = []
            
            for i, text in enumerate(texts):
                if text in self._cache:
                    cached_embeddings.append(self._cache[text])
                else:
                    texts_to_embed.append(text)
                    indices.append(i)
            
            if texts_to_embed:
                new_embeddings = self.model.embed(texts_to_embed)
                if normalize:
                    new_embeddings = self._normalize_embeddings(new_embeddings)
                    
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    self._cache[text] = embedding
                    
                all_embeddings = np.zeros((len(texts), self.model.get_dimension()))
                all_embeddings[indices] = new_embeddings
                if cached_embeddings:
                    remaining_indices = [i for i in range(len(texts)) if i not in indices]
                    all_embeddings[remaining_indices] = cached_embeddings
                    
                return all_embeddings
            
            return np.array(cached_embeddings)
        
        embeddings = self.model.embed(texts)
        if normalize:
            embeddings = self._normalize_embeddings(embeddings)
        return embeddings
    
    @staticmethod
    def _normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms
    
    def clear_cache(self):
        self._cache.clear()
