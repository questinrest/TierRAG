from fastapi import FastAPI
from api.auth.route import router as auth_router
from api.ingestion.route import router as upload_router
from api.generation.route import router as query_router

app = FastAPI(title="RAG Project API")

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {"message": "RAG Project API is running"}
