"""
Core Exceptions and Error Handlers.
"""
from backend.core.exceptions.exceptions import (
    AppException,
    WorkspaceNotFoundException,
    WorkspaceAlreadyExistsException,
    DocumentNotFoundException,
    InvalidFileTypeException,
    FileTooLargeException,
    EmbeddingGenerationException,
    VectorIndexException,
    GroqUnavailableException,
    QwenUnavailableException,
    InferenceException,
    ContextLengthExceededException,
    DatabaseException,
)
from backend.core.exceptions.handlers import register_exception_handlers

__all__ = [
    "AppException",
    "WorkspaceNotFoundException",
    "WorkspaceAlreadyExistsException",
    "DocumentNotFoundException",
    "InvalidFileTypeException",
    "FileTooLargeException",
    "EmbeddingGenerationException",
    "VectorIndexException",
    "GroqUnavailableException",
    "QwenUnavailableException",
    "InferenceException",
    "ContextLengthExceededException",
    "DatabaseException",
    "register_exception_handlers",
]
