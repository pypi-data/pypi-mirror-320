from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
here = Path(__file__).parent.resolve()


long_description = """
# Sports Vision

![PyPI](https://img.shields.io/pypi/v/sportsvision)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/sportsvision)

**Sports Vision** is a suite of research tools designed to advance computer vision applications in sports analytics. Developed with passion, this toolkit provides unified embeddings for both text and image data, enabling comprehensive multi-modal analysis.

## Features

- **Text Embeddings:** Generate high-quality text representations
- **Image Embeddings:** Extract meaningful features from images
- **Multi-Modal Embeddings:** Combine text and image data for holistic analysis
- **Unified Embeddings:** Consistent embedding space for diverse data types

## Installation

Install the package via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install sportsvision
```

**Note:** Ensure you have the appropriate version of PyTorch installed. Visit the official PyTorch website for installation instructions tailored to your system and CUDA version.

## Usage

Here's a step-by-step guide to using the sportsvision package for encoding texts and images.

### 1. Import Required Libraries

```python
import torch
from sportsvision.research.configs import UnifiedEmbedderConfig
from sportsvision.research.models import UnifiedEmbedderModel
from transformers import AutoConfig, AutoModel
from PIL import Image
```

### 2. Register Custom Config and Model with Transformers

To integrate the custom UnifiedEmbedderConfig and UnifiedEmbedderModel with Hugging Face's transformers library:

```python
# Register the custom configuration and model
AutoConfig.register("unified_embedder", UnifiedEmbedderConfig)
AutoModel.register(UnifiedEmbedderConfig, UnifiedEmbedderModel)
```

### 3. Load the Pretrained Model

Load the pretrained UnifiedEmbedderModel from the Hugging Face Hub:

```python
# Initialize the model from the pretrained repository
emb_model = AutoModel.from_pretrained("sportsvision/omniemb-v1")
```

### 4. Prepare the Model for Inference

```python
# Determine the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Move the model to the device
emb_model = emb_model.to(device)

# Set the model to evaluation mode
emb_model.eval()
```

### 5. Encode Texts

```python
# Sample texts
texts = [
    "Playoff season is exciting!",
    "Injury updates for the team."
]

# Encode texts to obtain embeddings
text_embeddings = emb_model.encode_texts(texts)

print("Text Embeddings:", text_embeddings)
```

### 6. Encode Images

```python
# Sample images
image_paths = [
    "path_to_image1.jpg",
    "path_to_image2.jpg"
]

# Load images using PIL
images = [Image.open(img_path).convert('RGB') for img_path in image_paths]

# Encode images to obtain embeddings
image_embeddings = emb_model.encode_images(images)

print("Image Embeddings:", image_embeddings)
```

## Complete Example

Here's a comprehensive example combining all the steps above:

```python
import torch
from sportsvision.research.configs import UnifiedEmbedderConfig
from sportsvision.research.models import UnifiedEmbedderModel
from transformers import AutoConfig, AutoModel
from PIL import Image

# Register the custom configuration and model
AutoConfig.register("unified_embedder", UnifiedEmbedderConfig)
AutoModel.register(UnifiedEmbedderConfig, UnifiedEmbedderModel)

# Initialize the model from the pretrained repository
emb_model = AutoModel.from_pretrained("sportsvision/omniemb-v1")

# Determine the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Move the model to the device
emb_model = emb_model.to(device)

# Set the model to evaluation mode
emb_model.eval()

# Sample texts
texts = [
    "Playoff season is exciting!",
    "Injury updates for the team."
]

# Encode texts to obtain embeddings
text_embeddings = emb_model.encode_texts(texts)
print("Text Embeddings:", text_embeddings)

# Sample images
image_paths = [
    "path_to_image1.jpg",
    "path_to_image2.jpg"
]

# Load images using PIL
images = [Image.open(img_path).convert('RGB') for img_path in image_paths]

# Encode images to obtain embeddings
image_embeddings = emb_model.encode_images(images)
print("Image Embeddings:", image_embeddings)
```

## Documentation

For more detailed information, tutorials, and advanced usage, please visit our [Hugging Face Documentation](https://huggingface.co/).

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please contact Varun Kodathala (varun@sportsvision.ai).
"""




setup(
    name="sportsvision",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "torch>=1.12.0,<3.0.0",        # Wide range but ensures compatibility
        "transformers>=4.26.0,<5.0.0",  # Stable CLIP support
        "pillow>=9.0.0,<12.0.0",       # Common version range
        "tqdm>=4.64.0,<5.0.0",         # Stable version
    ],
    description="Sports Vision Research Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Varun Kodathala",
    author_email="varun@sportsvision.ai",  # Corrected email typo
    url="https://huggingface.co/sportsvision",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.7, <4",
    include_package_data=True,  # Ensure non-Python files are included if specified in MANIFEST.in
    keywords=[
        "text embeddings",
        "image embeddings",
        "multi modal embeddings",
        "unified embeddings",
    ],
    license="MIT",
    zip_safe=False,  # Recommended to set to False if package contains data files
)
