from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    rerank: bool = False


class Source(BaseModel):
    source: str
    page: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    reference: List[Source]
    rerank: bool
    cache_tier: Optional[str] = None
