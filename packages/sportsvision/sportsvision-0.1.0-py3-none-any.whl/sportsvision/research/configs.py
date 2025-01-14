import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel, PretrainedConfig, CLIPProcessor, CLIPModel
from typing import List, Union, Optional
from PIL import Image
import io
from tqdm.auto import tqdm

class UnifiedEmbedderConfig(PretrainedConfig):
    model_type = "unified_embedder"
    
    def __init__(
        self,
        model_id: str = "openai/clip-vit-large-patch14",
        embedding_dim: int = 1536,
        **kwargs
    ):
        self.model_id = model_id
        self.embedding_dim = embedding_dim
        super().__init__(**kwargs)