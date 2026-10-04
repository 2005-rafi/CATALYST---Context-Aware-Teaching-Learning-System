import functools
from typing import Union
import json
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = Field(default="")
    HF_TOKEN: str = Field(default="")
    
    # Paths
    DATABASE_PATH: str = Field(default="storage/sqlite/app.db")
    UPLOADS_PATH: str = Field(default="storage/uploads/workspaces")
    FAISS_PATH: str = Field(default="storage/vectors/faiss")
    BM25_PATH: str = Field(default="storage/bm25")
    LOGS_PATH: str = Field(default="backend/logs")
    MODELS_CACHE_PATH: str = Field(default="storage/models")
    OFFLINE_MODE: bool = Field(default=True)
    
    # Models
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    CROSS_ENCODER_MODEL: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    GROQ_MODEL_MEDIUM: str = Field(default="llama-3.1-8b-instant")
    GROQ_MODEL_EXPERT: str = Field(default="llama-3.3-70b-versatile")
    LOCAL_MODEL_NAME: str = Field(default="qwen:0.5b")
    
    # Retrieval Config
    CHUNK_SIZE: int = Field(default=512)
    CHUNK_OVERLAP: int = Field(default=100)
    CHUNK_MIN_SIZE: int = Field(default=100)
    FAISS_TOP_K: int = Field(default=50)
    BM25_TOP_K: int = Field(default=50)
    RRF_CONSTANT: int = Field(default=60)
    RRF_TOP_N: int = Field(default=20)
    CROSS_ENCODER_TOP_N: int = Field(default=5)
    CROSS_ENCODER_MIN_SCORE: float = Field(default=0.60)
    CONTEXT_MAX_CHUNKS: int = Field(default=5)
    RECENT_CHAT_WINDOW: int = Field(default=5)
    SUMMARY_UPDATE_INTERVAL: int = Field(default=10)
    
    # Feature Flags
    ENABLE_BM25: bool = Field(default=True)
    ENABLE_RRF: bool = Field(default=True)
    ENABLE_CROSS_ENCODER: bool = Field(default=True)
    ENABLE_LOCAL_MODEL: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    ENVIRONMENT: str = Field(default="development")

    ALLOWED_ORIGINS: Union[list[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3002",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )
    PORT: int = Field(default=8000)

    @field_validator("ALLOWED_ORIGINS", mode="after")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            v_str = v.strip()
            if v_str == "*":
                return ["*"]
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        return ["*"]

    model_config = {
        "env_file": "secrets/.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    def faiss_workspace_path(self, workspace_id: str) -> str:
        return f"{self.FAISS_PATH}/{workspace_id}"

    def local_embedding_model_path(self) -> str:
        model_slug = self.EMBEDDING_MODEL.replace("/", "_")
        return f"{self.MODELS_CACHE_PATH}/embeddings/{model_slug}"

    def local_cross_encoder_path(self) -> str:
        model_slug = self.CROSS_ENCODER_MODEL.replace("/", "_")
        return f"{self.MODELS_CACHE_PATH}/cross_encoder/{model_slug}"

@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
