import uuid
import datetime
import time
from backend.services.memory.context_builder import ContextBuilder
from backend.services.memory.summarization_service import SummarizationService
from backend.repositories.sqlite.workspace_summary_repository import WorkspaceSummaryRepository
from backend.services.llm.response_formatter import ResponseFormatter
from backend.services.llm.prompt_builder import PromptBuilder
from backend.services.llm.failover_manager import FailoverManager
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.services.analytics.analytics_service import AnalyticsService
import logging

from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.core.exceptions.exceptions import WorkspaceNotFoundException

logger = logging.getLogger(__name__)
from backend.core.config.settings import get_settings

class ChatService:
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()
        self.context_builder = ContextBuilder()
        self.summarization_service = SummarizationService()
        self.summary_repo = WorkspaceSummaryRepository()
        
        self.formatter = ResponseFormatter()
        self.prompt_builder = PromptBuilder()
        self.failover_manager = FailoverManager()
        
        self.conversation_repo = ConversationRepository()
        self.analytics_service = AnalyticsService()
        self.settings = get_settings()

    def chat(self, workspace_id: str, query: str, model_type: str = "medium") -> tuple[dict, list[dict]]:
        if not self.workspace_repo.workspace_exists(workspace_id):
            raise WorkspaceNotFoundException(f"Workspace '{workspace_id}' not found.")
            
        start_time = time.time()
        logger.info("Query received", extra={"workspace_id": workspace_id, "query_length": len(query), "model_type": model_type})
        
        # 1. Build Context Package
        # Mode determines strictness and verbosity in the prompt
        context = self.context_builder.build(workspace_id, query, mode=model_type)
        
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        logger.info("Context built", extra={"workspace_id": workspace_id, "retrieved_chunks": len(context.retrieved_chunks), "confidence": context.confidence.level, "duration_ms": retrieval_time_ms})
        
        # 2. Determine actual LLM model and Generate Response (via failover)
        # Format Prompt
        messages = self.prompt_builder.build_from_context(context)
        
        # Generate Response
        raw_response, actual_model = self.failover_manager.generate(messages, mode=model_type)
        
        # Format and Append Sources
        clean_response = self.formatter.validate_and_clean(raw_response)
        response_text = self.formatter.append_sources(clean_response, context.sources)
            
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info("LLM generation completed", extra={"workspace_id": workspace_id, "model_used": actual_model, "response_length": len(response_text), "duration_ms": processing_time_ms})
        
        # 3. Save to Conversation History
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        user_msg_id = str(uuid.uuid4())
        asst_msg_id = str(uuid.uuid4())
        
        try:
            self.conversation_repo.save_message(
                message_id=user_msg_id,
                workspace_id=workspace_id,
                role="user",
                message=query,
                created_at=now,
                model_used=None,
                retrieval_chunks=0
            )
            asst_msg = self.conversation_repo.save_message(
                message_id=asst_msg_id,
                workspace_id=workspace_id,
                role="assistant",
                message=response_text,
                created_at=now,
                model_used=actual_model,
                retrieval_chunks=len(context.retrieved_chunks)
            )
            asst_msg["processing_time_ms"] = processing_time_ms
        except Exception as e:
            logger.warning(f"Could not persist conversation history (workspace may have been deleted concurrently): {e}")
            asst_msg = {
                "message_id": asst_msg_id,
                "workspace_id": workspace_id,
                "role": "assistant",
                "message": response_text,
                "created_at": now,
                "model_used": actual_model,
                "retrieval_chunks": len(context.retrieved_chunks),
                "processing_time_ms": processing_time_ms
            }
        
        # 4. Trigger Summarization (Background check)
        if self.summarization_service.should_summarize(workspace_id):
            summary = self.summarization_service.generate_summary(workspace_id)
            if summary:
                self.summary_repo.upsert_summary(workspace_id, summary)
        
        # 5. Update Analytics
        self.analytics_service.record_query(workspace_id, actual_model)
        
        # Format chunks for API return
        chunks_for_api = [c.model_dump() for c in context.retrieved_chunks]
        
        return asst_msg, chunks_for_api
