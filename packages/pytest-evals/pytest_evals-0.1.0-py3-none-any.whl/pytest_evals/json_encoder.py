import json
import dataclasses
from enum import Enum

try:
    from pydantic import BaseModel
    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False
    BaseModel = type(None)  # Create a dummy type that won't match anything


class AdvancedJsonEncoder(json.JSONEncoder):
    """JSON encoder that handles Pydantic models (if installed) and other special types."""

    def default(self, o):
        if HAVE_PYDANTIC and isinstance(o, BaseModel):
            return json.loads(o.model_dump_json()) # type: ignore
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o) # type: ignore
        if isinstance(o, Enum):
            return o.value
        return super().default(o)