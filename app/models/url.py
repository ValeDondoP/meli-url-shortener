from pydantic import BaseModel, Field, AnyUrl
from typing import Dict, Optional


class URLInput(BaseModel):
    original_url: AnyUrl

class URLInputUpdate(BaseModel):
    protocol: str
    domain: str
    path: Optional[str] = Field(None, description="Path should be a valid URL path.")
    params: Optional[Dict[str, str]] = Field(None, description="Params should be a dictionary of query parameters.")


class ToggleURL(BaseModel):
    enabled: bool
