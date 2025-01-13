"""**Load** module helps with serialization and deserialization."""

from aibaba-ai-core.load.dump import dumpd, dumps
from aibaba-ai-core.load.load import load, loads
from aibaba-ai-core.load.serializable import Serializable

__all__ = ["dumpd", "dumps", "load", "loads", "Serializable"]
