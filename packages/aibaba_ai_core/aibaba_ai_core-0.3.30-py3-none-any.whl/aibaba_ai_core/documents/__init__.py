"""**Document** module is a collection of classes that handle documents
and their transformations.

"""

from aibaba-ai-core.documents.base import Document
from aibaba-ai-core.documents.compressor import BaseDocumentCompressor
from aibaba-ai-core.documents.transformers import BaseDocumentTransformer

__all__ = ["Document", "BaseDocumentTransformer", "BaseDocumentCompressor"]
