from pydantic import BaseModel
from typing import Optional


class IngestResponse(BaseModel):
    message: str
    file: str
    chunks_inserted: Optional[int] = None
    namespace: Optional[str] = None


class DuplicateResponse(BaseModel):
    message: str
    file: str
