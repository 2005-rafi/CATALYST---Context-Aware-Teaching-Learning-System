import pytest
import sqlite3
import json
from backend.services.agents.retrieval_orchestrator_agent import RetrievalOrchestratorAgent
from backend.services.agents.pedagogical_synthesis_agent import PedagogicalSynthesisAgent
from backend.services.agents.master_orchestrator_agent import MasterOrchestratorAgent
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
from backend.services.curriculum.curriculum_path_manager import CurriculumPathManager
from backend.scripts.sanitize_memory_profiles import sanitize_database_memory_profiles
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository

class TestTopicKnowledgeExtractor:
    def setup_method(self):
        self.extractor = TopicKnowledgeExtractor()

    def test_noise_and_conversational_rejection(self):
        """Conversational filler, formatting, and broken sub-words must extract zero topics."""
        assert self.extractor.extract_topics("Explain in simple terms briefly") == []
        assert self.extractor.extract_topics("Please give me a summary overview and notes of chapter") == []
        assert self.extractor.extract_topics("What is the difference between these two?") == []
        assert self.extractor.extract_topics("Tell me details and definitions") == []

    def test_authentic_domain_topic_extraction(self):
        """Genuine syllabus and pedagogical concepts must be accurately extracted in Title Case."""
        topics = self.extractor.extract_topics("Explain human reproductive system and spermatogenesis")
        assert "Human Reproduction" in topics
        assert "Spermatogenesis" in topics

        topics2 = self.extractor.extract_topics("What is the structure of ovum and oogenesis?")
        assert "Structure of Ovum" in topics2
        assert "Oogenesis" in topics2

        topics3 = self.extractor.extract_topics("Explain environmental issues and air pollution")
        assert "Environmental Issues" in topics3
        assert "Air Pollution" in topics3

    def test_is_valid_topic_filter(self):
        """is_valid_topic must return False for all noise words and True for valid concepts."""
        junk = ["simple", "term", "brief", "chapte", "able", "agra", "plain", "acteria", "less", "evaluation"]
        for word in junk:
            assert self.extractor.is_valid_topic(word) is False, f"Failed for junk word: {word}"

        valid = ["Human Reproduction", "Spermatogenesis", "Circulatory System", "Digestive System", "Contraception", "DNA Replication"]
        for topic in valid:
            assert self.extractor.is_valid_topic(topic) is True, f"Failed for valid topic: {topic}"

class TestCurriculumPathManager:
    def setup_method(self):
        self.manager = CurriculumPathManager()

    def test_learning_path_telemetry(self):
        topic_familiarity = {
            "Contraception": {"familiarity_score": 0.5, "query_count": 2},
            "Circulation": {"familiarity_score": 0.85, "query_count": 4},
            "simple": {"familiarity_score": 0.1, "query_count": 1} # Junk key to test defensive filter
        }
        telemetry = self.manager.get_learning_path_telemetry(
            workspace_id="test-workspace",
            topic_familiarity=topic_familiarity,
            struggle_topics=[]
        )
        assert telemetry["explored_count"] == 2 # Only valid topics counted
        assert telemetry["mastered_count"] == 1 # Circulation >= 0.8
        assert len(telemetry["recommended_next"]) > 0

class TestThreeAgentArchitecture:
    def setup_method(self):
        self.agent1 = RetrievalOrchestratorAgent()
        self.agent2 = PedagogicalSynthesisAgent()
        self.agent3 = MasterOrchestratorAgent()
        self.workspace_repo = WorkspaceRepository()

    def test_agent_1_retrieval_orchestrator(self):
        """Agent 1 intent classification and topic extraction must operate cleanly."""
        intent = self.agent1.reformulator.classify_intent("Explain human reproduction in detail")
        assert intent in ["CONCEPTUAL", "STRUCTURAL_OVERVIEW", "TOPICAL_CONCEPT", "FACTOID"]

        topics = self.agent1.reformulator.extract_topics("Explain human reproduction and spermatogenesis")
        assert "Human Reproduction" in topics

    def test_agent_2_pedagogical_synthesizer(self):
        """Agent 2 has low temperature and formatter ready."""
        assert self.agent2.factual_temperature == 0.10
        assert self.agent2.prompt_builder is not None
        assert self.agent2.formatter is not None

    def test_agent_3_master_orchestrator_integration(self):
        """Agent 3 orchestrates Agent 1 and Agent 2 with topic intelligence."""
        # Find active workspace if any
        workspaces = self.workspace_repo.get_all_workspaces()
        if not workspaces:
            pytest.skip("No workspaces found in SQLite to run integration query")

        workspace_id = workspaces[0]["workspace_id"]
        asst_msg, chunks = self.agent3.orchestrate_chat(
            workspace_id=workspace_id,
            query="Explain human reproduction and contraception in brief",
            mode="medium"
        )
        assert asst_msg is not None
        assert len(asst_msg["message"]) > 50
        assert asst_msg["role"] == "assistant"
        assert isinstance(chunks, list)
