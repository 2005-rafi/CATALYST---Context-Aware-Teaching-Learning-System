class AppException(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class WorkspaceNotFoundException(AppException):
    def __init__(self, detail: str = "Workspace not found"):
        super().__init__(detail, status_code=404)

class DocumentNotFoundException(AppException):
    def __init__(self, detail: str = "Document not found"):
        super().__init__(detail, status_code=404)

class WorkspaceAlreadyExistsException(AppException):
    def __init__(self, detail: str = "Workspace already exists"):
        super().__init__(detail, status_code=409)

class InvalidFileTypeException(AppException):
    def __init__(self, detail: str = "Invalid file type"):
        super().__init__(detail, status_code=400)

class FileTooLargeException(AppException):
    def __init__(self, detail: str = "File too large"):
        super().__init__(detail, status_code=400)

class IngestionFailedException(AppException):
    def __init__(self, detail: str = "Document ingestion failed"):
        super().__init__(detail, status_code=500)

class RetrievalFailedException(AppException):
    def __init__(self, detail: str = "Context retrieval failed"):
        super().__init__(detail, status_code=500)

class GroqUnavailableException(AppException):
    def __init__(self, detail: str = "Groq API is unavailable"):
        super().__init__(detail, status_code=503)

class QwenUnavailableException(AppException):
    def __init__(self, detail: str = "Local Qwen API is unavailable"):
        super().__init__(detail, status_code=503)

class EmbeddingGenerationException(AppException):
    def __init__(self, detail: str = "Embedding generation failed"):
        super().__init__(detail, status_code=500)

class VectorIndexException(AppException):
    def __init__(self, detail: str = "Vector index operation failed"):
        super().__init__(detail, status_code=500)

class InferenceException(AppException):
    def __init__(self, detail: str = "Inference execution failed"):
        super().__init__(detail, status_code=500)

class ContextLengthExceededException(AppException):
    def __init__(self, detail: str = "Context length exceeded maximum limit"):
        super().__init__(detail, status_code=400)

class DatabaseException(AppException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail, status_code=500)
