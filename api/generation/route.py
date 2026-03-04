from fastapi import APIRouter, Depends, HTTPException
from api.generation.datamodels import QueryRequest, QueryResponse
from api.generation.services import retrieve_chunks, build_sources, get_answer
from api.ingestion.services import get_current_user

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, username: str = Depends(get_current_user)):
    try:
        namespace = username
        related_docs = retrieve_chunks(
            query=request.query,
            namespace=namespace,
            rerank=request.rerank
        )
        sources = build_sources(related_docs)
        answer = get_answer(query=request.query, chunks=related_docs)
        return QueryResponse(
            answer=answer,
            reference=sources,
            rerank=request.rerank
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )