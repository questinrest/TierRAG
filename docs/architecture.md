# Architecture Document

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system with:

- ✅ User registration & login (MongoDB)
- ✅ JWT-based authentication (HTTPBearer)
- ✅ Namespace isolation in Pinecone (per-user)
- ✅ Parent-child document chunking
- ✅ Document ingestion with duplicate detection
- 🔲 Multi-tier caching (Exact, Semantic, Retrieval)
- ✅ Retrieval with optional reranking
- ✅ LLM-based answer generation

---

## System Architecture

```mermaid
flowchart TB
    subgraph CLIENT["Client"]
        SW["Swagger UI / Frontend"]
    end

    subgraph API["FastAPI Application"]
        MAIN["main.py"]
        subgraph AUTH["api/auth ✅"]
            REG["POST /api/admin/register"]
            LOGIN["POST /api/admin/login"]
        end
        subgraph INGEST["api/ingestion ✅"]
            UPLOAD["POST /upload"]
        end
        subgraph QUERY["api/generation ✅"]
            QRY["POST /query"]
        end
    end

    subgraph CORE["src/ modules"]
        CONFIG["config.py ✅"]
        CHUNK["chunking/parent_child.py ✅"]
        EMBED["embedding/embed.py ✅"]
        CACHE["caching/ 🔲"]
        RET["retrieval/ ✅"]
        GEN["generation/ ✅"]
        DB["database/ 🔲"]
        UTIL["utils/ 🔲"]
    end

    subgraph STORAGE["External Storage"]
        MONGO[("MongoDB Atlas")]
        PINE[("Pinecone")]
        REDIS[("Redis 🔲")]
        LLM["LLM API ✅"]
    end

    SW --> MAIN
    MAIN --> AUTH
    MAIN --> INGEST
    MAIN --> QUERY

    REG --> CONFIG
    LOGIN --> CONFIG
    CONFIG --> MONGO

    UPLOAD --> CHUNK
    CHUNK --> EMBED
    EMBED --> PINE

    QRY --> CACHE
    CACHE --> RET
    RET --> PINE
    RET --> GEN
    GEN --> LLM
    CACHE --> REDIS
```

---

# 1. User Registration ✅

```mermaid
flowchart TD
    A["User"] --> B["POST /api/admin/register"]
    B --> C{"Username exists in MongoDB?"}
    C -- Yes --> D["Return: User already exists"]
    C -- No --> E["Hash password with bcrypt"]
    E --> F["Store in devlogins collection"]
    F --> G["Return: Registration Successful"]
```

**Implemented in:** `api/auth/route.py`, `api/auth/services.py`

---

# 2. User Login ✅

```mermaid
flowchart TD
    A["User"] --> B["POST /api/admin/login"]
    B --> C{"Username exists?"}
    C -- No --> D["Return: Invalid username or password"]
    C -- Yes --> E["Verify bcrypt hash"]
    E --> F{"Password matches?"}
    F -- No --> D
    F -- Yes --> G["Generate JWT token"]
    G --> H["Return: access_token + bearer type"]
```

**Implemented in:** `api/auth/route.py`, `api/auth/services.py`
- Token expires in 24 hours
- Algorithm: HS256

---

# 3. Document Ingestion ✅

```mermaid
flowchart TD
    A["Authenticated User"] --> B["POST /upload with file"]
    B --> C["HTTPBearer token validation"]
    C --> D{"Valid JWT?"}
    D -- No --> E["401 Unauthorized"]
    D -- Yes --> F["Extract username from JWT"]
    F --> G{"File type allowed?"}
    G -- No --> H["400: Unsupported file type"]
    G -- Yes --> I["Save file to uploads/"]

    I --> J["Parent-child chunking pipeline"]

    subgraph CHUNKING["Chunking Pipeline"]
        J --> K["Load document via PyMuPDF/TextLoader"]
        K --> L["Split into parent chunks"]
        L --> M["Split parents into child chunks"]
        M --> N["Map children to parent IDs"]
        N --> O["Compute SHA256 file hash"]
    end

    O --> P{"Duplicate hash in namespace?"}
    P -- Yes --> Q["Return: Document already exists"]
    P -- No --> R["Batch upsert to Pinecone"]
    R --> S["Return: Success + chunks_inserted count"]
```

**Implemented in:** `api/ingestion/route.py`, `src/chunking/parent_child.py`, `src/embedding/embed.py`

### Chunking Details
| Parameter | Default |
|-----------|---------|
| Parent chunk size | 1000 |
| Parent chunk overlap | 200 |
| Child chunk size | 200 |
| Child chunk overlap | 20 |

### Pinecone Configuration
| Setting | Value |
|---------|-------|
| Index name | devrag |
| Embedding model | llama-text-embed-v2 |
| Cloud | AWS (us-east-1) |
| Batch size | 96 |

---

# 4. Query Pipeline ✅

```mermaid
flowchart TD
    A["User Query + Namespace"] --> B["Validate Request"]
    B --> C["Exact Cache - Tier 1"]
    C -->|Hit| D["Return Cached Answer"]
    C -->|Miss| E["Semantic Cache - Tier 2"]
    E -->|Hit| D
    E -->|Miss| F["Retrieval Cache - Tier 3"]
    F -->|Hit| D
    F -->|Miss| G{"Rerank Enabled?"}

    G -- Yes --> H["Retrieve + Rerank"]
    G -- No --> I["Retrieve Top-K"]

    H --> J["Build Context from Parent Chunks"]
    I --> J

    J --> K["Generate Answer via LLM"]
    K --> L["Store in Cache"]
    L --> D

    style C fill:#333,stroke:#888,stroke-dasharray: 5 5
    style E fill:#333,stroke:#888,stroke-dasharray: 5 5
    style F fill:#333,stroke:#888,stroke-dasharray: 5 5
    style L fill:#333,stroke:#888,stroke-dasharray: 5 5
```

---

# 5. Data Storage

```mermaid
erDiagram
    DEVLOGINS {
        ObjectId _id PK
        string username
        string hashed_password
        boolean namespace
    }

    PINECONE_RECORDS {
        string _id PK
        string chunk_text
        string parent_id
        string source
        int page
        string source_hash_value
        vector embedding
    }

    DEVLOGINS ||--o{ PINECONE_RECORDS : "namespace = username"
```

### Storage Responsibilities

| Store | Technology | Status |
|-------|-----------|--------|
| User credentials | MongoDB Atlas (`devlogins`) | ✅ Implemented |
| Vector chunks | Pinecone (`devrag` index) | ✅ Implemented |
| Cached responses | Redis | 🔲 Planned |
| LLM generation | Groq API | ✅ Implemented |

---

# 6. Module Status

| Module | Files | Status |
|--------|-------|--------|
| `api/auth/` | route, services, datamodels | ✅ Implemented |
| `api/ingestion/` | route, services, datamodels | ✅ Implemented |
| `src/config.py` | MongoDB, Pinecone, JWT config | ✅ Implemented |
| `src/chunking/` | parent_child.py | ✅ Implemented |
| `src/embedding/` | embed.py | ✅ Implemented |
| `src/caching/` | exact_cache, semantic_cache, retrieval_cache | 🔲 Empty stubs |
| `src/retrieval/` | retriever, reranker | ✅ Implemented |
| `src/generation/` | generator | ✅ Implemented |
| `src/database/` | models, crud, connection | 🔲 Empty stubs |
| `src/utils/` | embeddings, logger | 🔲 Empty stubs |