import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel, PretrainedConfig, CLIPProcessor, CLIPModel
from typing import List, Union, Optional
from PIL import Image
import io
from tqdm.auto import tqdm
from .configs import UnifiedEmbedderConfig

class UnifiedEmbedderModel(PreTrainedModel):
    config_class = UnifiedEmbedderConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        
        # Initialize CLIP model and processor
        self.clip = CLIPModel.from_pretrained(config.model_id)
        self.processor = CLIPProcessor.from_pretrained(config.model_id)
        
        # Get CLIP's native dimension
        self.clip_dim = self.clip.config.projection_dim
        
        # Initialize projection layers
        projection_layers = [
            nn.Linear(self.clip_dim, config.embedding_dim),
            nn.LayerNorm(config.embedding_dim),
            nn.GELU(),
            nn.Linear(config.embedding_dim, config.embedding_dim),
            nn.LayerNorm(config.embedding_dim)
        ] if self.clip_dim != config.embedding_dim else [nn.Identity()]
        
        self.projector = nn.Sequential(*projection_layers)
        
    def _process_long_text(
        self,
        text: str,
        max_chunk_length: int = 77,
        stride: int = 50
    ) -> torch.Tensor:
        """Process long text by splitting into overlapping chunks and averaging embeddings."""
        tokens = self.processor.tokenizer(
            text,
            padding=False,
            truncation=False,
            return_tensors="pt"
        )

        if tokens['input_ids'].shape[1] <= max_chunk_length:
            tokens = {k: v.to(self.device) for k, v in tokens.items()}
            with torch.no_grad():
                features = self.clip.get_text_features(**tokens)
            return features

        # Split into overlapping chunks
        input_ids = tokens['input_ids'][0]
        attention_mask = tokens['attention_mask'][0]

        chunks_ids = []
        chunks_mask = []

        start_idx = 0
        while start_idx < len(input_ids):
            end_idx = min(start_idx + max_chunk_length, len(input_ids))
            chunk_ids = input_ids[start_idx:end_idx]
            chunk_mask = attention_mask[start_idx:end_idx]

            # Pad if necessary
            if len(chunk_ids) < max_chunk_length:
                padding_length = max_chunk_length - len(chunk_ids)
                chunk_ids = F.pad(chunk_ids, (0, padding_length), value=self.processor.tokenizer.pad_token_id)
                chunk_mask = F.pad(chunk_mask, (0, padding_length), value=0)

            chunks_ids.append(chunk_ids)
            chunks_mask.append(chunk_mask)

            start_idx += stride

        # Process chunks
        chunks_ids = torch.stack(chunks_ids).to(self.device)
        chunks_mask = torch.stack(chunks_mask).to(self.device)

        with torch.no_grad():
            features = []
            for i in range(0, len(chunks_ids), self.batch_size):
                batch_ids = chunks_ids[i:i + self.batch_size]
                batch_mask = chunks_mask[i:i + self.batch_size]
                batch_features = self.clip.get_text_features(
                    input_ids=batch_ids,
                    attention_mask=batch_mask
                )
                features.append(batch_features)

            features = torch.cat(features, dim=0)

        # Average embeddings
        return features.mean(dim=0, keepdim=True)

    @torch.no_grad()
    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> torch.Tensor:
        """Encode a list of texts into unified embeddings."""
        all_features = []
        iterator = tqdm(range(0, len(texts), batch_size)) if show_progress else range(0, len(texts), batch_size)

        for i in iterator:
            batch_texts = texts[i:i + batch_size]
            batch_features = []

            for text in batch_texts:
                features = self._process_long_text(text)
                batch_features.append(features)

            if batch_features:
                batch_features = torch.cat(batch_features, dim=0)
                batch_features = self.projector(batch_features)
                all_features.append(F.normalize(batch_features, dim=-1))

        return torch.cat(all_features, dim=0) if all_features else torch.empty(0, self.projector[-1].normalized_shape[0])

    @torch.no_grad()
    def encode_images(
        self,
        images: List[Union[str, bytes, Image.Image]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> torch.Tensor:
        """Encode a list of images into unified embeddings."""
        all_features = []

        # Convert images to PIL
        pil_images = []
        for img in images:
            if isinstance(img, str):
                pil_images.append(Image.open(img).convert('RGB'))
            elif isinstance(img, bytes):
                pil_images.append(Image.open(io.BytesIO(img)).convert('RGB'))
            elif isinstance(img, Image.Image):
                pil_images.append(img.convert('RGB'))
            else:
                raise ValueError(f"Unsupported image type: {type(img)}")

        iterator = tqdm(range(0, len(pil_images), batch_size)) if show_progress else range(0, len(pil_images), batch_size)

        for i in iterator:
            batch_images = pil_images[i:i + batch_size]
            inputs = self.processor(
                images=batch_images,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            features = self.clip.get_image_features(**inputs)
            features = self.projector(features)
            all_features.append(F.normalize(features, dim=-1))

        return torch.cat(all_features, dim=0) if all_features else torch.empty(0, self.projector[-1].normalized_shape[0])

    def compute_similarity(
        self,
        embeddings1: torch.Tensor,
        embeddings2: torch.Tensor
    ) -> torch.Tensor:
        """Compute cosine similarity between two sets of embeddings."""
        return torch.matmul(embeddings1, embeddings2.T)

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        pixel_values=None,
        return_loss=False,
        **kwargs
    ):
        """Forward pass handling both text and image inputs."""
        outputs = {}
        
        if input_ids is not None and attention_mask is not None:
            text_features = self.clip.get_text_features(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            text_embeddings = self.projector(text_features)
            outputs["text_embeddings"] = F.normalize(text_embeddings, dim=-1)
            
        if pixel_values is not None:
            image_features = self.clip.get_image_features(pixel_values=pixel_values)
            image_embeddings = self.projector(image_features)
            outputs["image_embeddings"] = F.normalize(image_embeddings, dim=-1)
            
        return outputs