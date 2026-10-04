"""Analytics API schemas — Pydantic request/response models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class AnalyticsResponse(BaseModel):
    workspace_id: str
    total_queries: int
    total_documents: int
    total_chunks: int
    storage_used_mb: float
    groq_requests: int
    local_model_requests: int
    last_updated: Optional[str] = None


class DailyActivityPoint(BaseModel):
    date: str
    label: str
    query_count: int
    message_count: int


class TopicMasteryItem(BaseModel):
    topic: str
    familiarity_score: float  # 0.0 to 1.0
    familiarity_percent: int  # 0 to 100
    level: str  # Beginner, Proficient, Mastered
    query_count: int
    is_struggling: bool = False


class DocumentMetricItem(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    file_size_mb: float
    total_chunks: int
    figures_count: int = 0
    upload_time: str
    processing_status: str


class FigureMetricSummary(BaseModel):
    total_figures: int
    by_type: Dict[str, int] = Field(default_factory=dict)
    sample_captions: List[str] = Field(default_factory=list)


class DetailedAnalyticsResponse(BaseModel):
    workspace_id: str
    workspace_name: str
    created_at: str
    last_updated: Optional[str] = None
    
    # Core KPI Counters
    total_queries: int
    total_documents: int
    total_chunks: int
    storage_used_mb: float
    groq_requests: int
    local_model_requests: int
    
    # RAG Retrieval & Ingestion Telemetry
    avg_chunks_per_query: float = 0.0
    total_sessions: int = 0
    total_messages: int = 0
    
    # Cognitive Profile & Topic Mastery
    learning_style: str = "balanced"
    preferred_mode: str = "medium"
    topic_mastery: List[TopicMasteryItem] = Field(default_factory=list)
    struggle_topics: List[str] = Field(default_factory=list)
    
    # Time-series Activity
    activity_timeline: List[DailyActivityPoint] = Field(default_factory=list)
    
    # Document Breakdown
    documents: List[DocumentMetricItem] = Field(default_factory=list)
    
    # Visual Figures Telemetry
    figures_summary: FigureMetricSummary = Field(default_factory=lambda: FigureMetricSummary(total_figures=0))
