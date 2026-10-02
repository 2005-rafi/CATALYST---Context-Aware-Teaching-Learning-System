from backend.providers.groq.groq_provider import GroqProvider
from backend.providers.qwen.qwen_provider import QwenProvider
from backend.providers.embeddings.embedding_provider import get_embedding_provider
from backend.repositories.sqlite.database import db_connection
import logging

logger = logging.getLogger(__name__)

class HealthService:
    def __init__(self):
        self.groq = GroqProvider()
        self.qwen = QwenProvider()

    def check_database(self) -> dict:
        try:
            with db_connection() as conn:
                conn.execute("SELECT 1").fetchone()
            return {"status": "ok", "detail": "SQLite database connected (WAL mode active)."}
        except Exception as e:
            logger.error(f"Health check database error: {e}")
            return {"status": "error", "detail": str(e)}

    def check_embedding_model(self) -> dict:
        try:
            provider = get_embedding_provider()
            if provider.model is not None:
                dim = (
                    provider.model.get_embedding_dimension()
                    if hasattr(provider.model, "get_embedding_dimension")
                    else provider.model.get_sentence_embedding_dimension()
                )
                return {
                    "status": "ok", 
                    "detail": f"Embedding model '{provider.model_name}' loaded ({dim}-dimensional)."
                }
            return {"status": "error", "detail": "Embedding model not initialized in memory."}
        except Exception as e:
            logger.error(f"Health check embedding error: {e}")
            return {"status": "error", "detail": str(e)}

    def check_groq(self) -> dict:
        return self.groq.get_diagnostics()

    def check_qwen(self) -> dict:
        return self.qwen.get_diagnostics()

    def get_full_health(self) -> dict:
        subsystems = {
            "database": self.check_database(),
            "embedding": self.check_embedding_model(),
            "groq": self.check_groq(),
            "qwen": self.check_qwen()
        }
        
        # Core subsystems required for basic operations
        core_healthy = (
            subsystems["database"]["status"] == "ok" and 
            subsystems["embedding"]["status"] == "ok"
        )
        
        # LLM availability
        groq_ok = subsystems["groq"]["status"] == "ok"
        qwen_ok = subsystems["qwen"]["status"] == "ok"
        
        if core_healthy and groq_ok and qwen_ok:
            overall = "healthy"
        elif core_healthy and (groq_ok or qwen_ok):
            overall = "operational"
        elif core_healthy:
            overall = "operational"
        else:
            overall = "degraded"
                
        return {
            "status": overall,
            "version": "1.0.0",
            "subsystems": subsystems
        }
