import logging
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.core.exceptions.exceptions import WorkspaceNotFoundException
from backend.services.agents.master_orchestrator_agent import MasterOrchestratorAgent
from backend.services.memory.conversation_intelligence_manager import ConversationIntelligenceManager
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class ChatService:
    """
    Application Chat Service.
    Acts as the entry boundary for chat operations, delegating pure orchestration,
    supervised retry/failover, and cognitive knowledge tracking to the MasterOrchestratorAgent (Agent 3).
    """
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()
        self.master_orchestrator = MasterOrchestratorAgent()
        self.ci_manager = ConversationIntelligenceManager()
        self.settings = get_settings()

    def chat(
        self,
        workspace_id: str,
        query: str,
        model_type: str = "medium",
        session_id: str | None = None
    ) -> tuple[dict, list[dict]]:
        if not self.workspace_repo.workspace_exists(workspace_id):
            raise WorkspaceNotFoundException(f"Workspace '{workspace_id}' not found.")

        # Resolve or auto-create active session if session_id not specified
        if not session_id:
            try:
                active_session = self.ci_manager.session_manager.get_or_create_active_session(workspace_id)
                session_id = active_session.get("session_id")
            except Exception as e:
                logger.warning(f"Could not resolve active session for workspace {workspace_id}: {e}")

        # Delegate execution to Agent 3: Master Orchestrator Agent
        return self.master_orchestrator.orchestrate_chat(
            workspace_id=workspace_id,
            query=query,
            mode=model_type,
            session_id=session_id
        )

    def chat_stream(
        self,
        workspace_id: str,
        query: str,
        model_type: str = "medium",
        session_id: str | None = None
    ):
        if not self.workspace_repo.workspace_exists(workspace_id):
            raise WorkspaceNotFoundException(f"Workspace '{workspace_id}' not found.")

        return self.master_orchestrator.orchestrate_stream(
            workspace_id=workspace_id,
            query=query,
            mode=model_type,
            session_id=session_id
        )

