from pydantic import BaseModel, Field, AnyUrl
from typing import Dict, Optional

""""
class URL(BaseModel):
    original_url: HttpUrl
    short_url: str
    enabled: bool = True
    created_at = Field(default=datetime.now())
    visit_count: int = 0
    last_visit: datetime = Field(default=datetime.now)

"""
class URLInput(BaseModel):
    original_url: AnyUrl

class URLInputUpdate(BaseModel):
    protocol: str
    domain: str
    path: Optional[str] = Field(None, description="Path should be a valid URL path.")
    params: Optional[Dict[str, str]] = Field(None, description="Params should be a dictionary of query parameters.")


class ToggleURL(BaseModel):
    enabled: bool
