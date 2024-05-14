from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class URL(BaseModel):
    """
    Model representing a URL in the application.
    """

    original_url: HttpUrl
    short_url: str
    enabled: bool = True
    created_at = Field(default=datetime.now())
    visit_count: int = 0
    last_visit: datetime = Field(default=datetime.now)


class URLInput(BaseModel):
    original_url: HttpUrl

class ToggleURL(BaseModel):
    enabled: bool
