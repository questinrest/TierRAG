from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.ingestion.datamodels import IngestResponse, DuplicateResponse
from fastapi.security import HTTPBearer
import hashlib
import os
from api.ingestion.services import get_current_user
from src.embedding.embed import upsert_chunks, duplicate_exists
from src.chunking.parent_child import ingest
from pathlib import Path
import shutil

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    """
    Upload document and index it in Pinecone.
    Namespace = username
    """

    allowed_types = {".pdf", ".txt"}

    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    # save file
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    namespace = username

    # run parent-child chunking pipeline
    records, parents = ingest(file_path)

    # duplicate detection
    source_hash = records[0]["source_hash_value"]

    if duplicate_exists(namespace, source_hash):
        return {
            "message": "Document already exists in namespace",
            "file": file.filename
        }

    # upsert into Pinecone
    inserted = upsert_chunks(records, namespace)

    return {
        "message": "Document uploaded and indexed successfully",
        "file": file.filename,
        "chunks_inserted": inserted,
        "namespace": namespace
    }