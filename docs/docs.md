# Problem Statement
Modern AI-powered chatbot systems have significantly improved access to information; however, they continue to face several limitations when handling large volumes of user-uploaded documents and maintaining contextual conversations. Most traditional chatbot solutions rely heavily on the language model's internal knowledge and limited context window, making it difficult to accurately process large research papers, technical reports, academic documents, and other extensive sources of information. As document size and quantity increase, the ability of the AI system to retrieve relevant information efficiently decreases, often resulting in incomplete responses, irrelevant answers, or hallucinated content.

Another major challenge is the lack of long-term contextual understanding across conversations. Conventional chatbot systems typically process each user interaction independently, limiting their ability to provide context-aware responses based on previous discussions. Furthermore, many existing solutions require cloud-based infrastructure and subscription-based services to support document uploads, advanced retrieval capabilities, and larger context windows, creating accessibility and cost barriers for students, researchers, and academic users.

The problem becomes more complex when users need to manage multiple independent research domains simultaneously. Documents belonging to different subjects, projects, or research areas must remain isolated while still supporting accurate information retrieval and conversational continuity within each domain. Therefore, there is a need for an intelligent document-centric chatbot system capable of processing large volumes of uploaded documents, maintaining workspace-specific context, retrieving highly relevant information efficiently, minimizing hallucinations, and providing accurate responses with minimal latency while remaining accessible through a cost-effective architecture.

# Overview

The proposed system is an AI-powered document intelligence platform that combines Natural Language Processing (NLP), Information Retrieval (IR), Retrieval-Augmented Generation (RAG), and Large Language Models (LLMs) to provide context-aware conversational assistance over user-uploaded documents. The system enables users to create isolated workspaces, upload multiple documents, and interact with an AI assistant capable of answering questions based on the contents of those documents while maintaining conversational context.

The architecture is designed around a retrieval-first approach, where the majority of intelligence is handled through document processing, semantic search, query reformulation, hybrid retrieval, reranking, and contextual memory management before involving the language model. User-uploaded documents undergo a structured ingestion pipeline consisting of text extraction, chunk generation, embedding creation, and vector indexing. During query execution, the system employs NLP-driven query enhancement, hybrid retrieval using FAISS and BM25, Reciprocal Rank Fusion (RRF), and Cross-Encoder reranking to identify the most relevant document chunks before constructing context for the language model.

To ensure workspace isolation and contextual continuity, the system maintains separate document repositories, retrieval indexes, metadata, and conversation histories for each workspace. The AI layer utilizes Groq-hosted language models for medium and expert reasoning modes, while a locally hosted Qwen2.5-3B-Instruct model serves as a fallback mechanism and lightweight inference engine. Through this architecture, the system aims to deliver accurate, context-aware, and efficient responses while minimizing computational overhead, reducing hallucinations, and maintaining a seamless user experience.
# Proposed Solution

To address the limitations of conventional chatbot systems, this project proposes a retrieval-centric AI architecture that integrates NLP, Information Retrieval, Retrieval-Augmented Generation, and modern language models into a unified document intelligence platform. The system is designed around five primary backend pipelines: Workspace Management, Document Ingestion, Information Retrieval, Context and Memory Management, and LLM Generation. Each pipeline operates independently with clearly defined responsibilities, ensuring maintainability, scalability, and ease of debugging while minimizing architectural complexity.

Users interact with the system through isolated workspaces where documents can be uploaded, processed, and stored independently. During ingestion, uploaded documents are transformed through a structured pipeline consisting of text extraction, tokenization, chunking, semantic embedding generation, and vector indexing. The processed information is stored using FAISS for semantic retrieval and SQLite for structured metadata and conversational history management. To maximize retrieval accuracy, the system employs a hybrid retrieval strategy combining FAISS-based semantic search and BM25-based lexical search. Retrieved results are merged using Reciprocal Rank Fusion and optionally refined using Cross-Encoder reranking to identify the most relevant context for the user's query.

The system further enhances retrieval quality through NLP-based query reformulation, enabling better semantic understanding of user intent. Contextual awareness is maintained through workspace-specific memory management, recent conversation tracking, and conversation summarization mechanisms. Once relevant information is retrieved, the language model acts as the final reasoning layer by generating responses grounded in retrieved evidence rather than relying solely on its pretrained knowledge. When relevant information is unavailable within uploaded documents, the system transparently informs the user and supplements responses with general knowledge where appropriate. This architecture minimizes hallucinations, improves response accuracy, supports large document collections, and delivers an efficient AI-assisted research and knowledge exploration experience while remaining suitable for free-tier development environments and local deployment scenarios.

# Architecture

## Backend Architecture

The backend follows a layered architecture combined with a pipeline-oriented design to ensure separation of concerns, maintainability, and scalability while avoiding unnecessary complexity. The system is divided into five independent pipelines: Workspace Management, Document Ingestion, Information Retrieval, Context & Memory Management, and LLM Generation. Each pipeline has a clearly defined responsibility and communicates through service orchestration rather than direct coupling.

The FastAPI server acts as the central orchestration layer and serves as the single entry point for all frontend requests. It is responsible for request validation, workflow coordination, error handling, logging, health monitoring, and response formatting. Internally, the backend follows the structure API Layer → Service Layer → Repository Layer → Storage Layer. The Service Layer contains the core business logic, while Repository components manage interactions with SQLite, FAISS, and retrieval indexes. The retrieval subsystem combines NLP-based query reformulation, FAISS semantic retrieval, BM25 lexical retrieval, Reciprocal Rank Fusion, Cross-Encoder reranking, duplicate suppression, and context compression before forwarding information to the language model layer.

The AI subsystem is intentionally designed as the final reasoning layer rather than the primary intelligence source. Most contextual understanding is achieved through retrieval and ranking mechanisms before the LLM is invoked. Groq-hosted models provide medium and expert reasoning capabilities, while Qwen2.5-3B-Instruct acts as a local fallback and lightweight inference model to ensure uninterrupted operation.

## Frontend Architecture

The frontend is developed using Next.js and follows a feature-based architecture combined with a layered frontend design. The architecture consists of Presentation Layer, State Management Layer, API Service Layer, and Shared Core Layer. The Presentation Layer contains reusable Bento Grid components such as Workspace Management, Chat Interface, Document Upload Manager, Analytics Dashboard, AI Status Monitor, and System Configuration Panels.

The State Management Layer serves as the centralized source of truth for workspace state, document state, chat state, analytics state, and system status. The API Service Layer abstracts all backend communication through strongly typed service modules, ensuring UI components remain independent from backend implementation details. The Shared Core Layer contains reusable utilities, models, constants, validation logic, and design system components.

The frontend communicates exclusively with the FastAPI orchestration layer, allowing all backend complexity to remain hidden from users. This architecture promotes code reusability, efficient rendering, workspace isolation, minimal re-renders, and seamless user experience while maintaining low resource consumption.

### Parsing of Output and display
Text parsing should be treated as a dedicated transformation layer between retrieval and generation rather than a simple string concatenation process. After a user uploads a PDF or DOCX, the ingestion pipeline extracts raw text, removes formatting noise, normalizes whitespace, preserves structural elements such as headings, tables, bullet points, and paragraphs, and then generates chunks with associated metadata. Each chunk should carry contextual information such as `workspace_id`, `document_id`, `chunk_id`, source filename, page number, section heading, and chunk text. During retrieval, the system should not send raw chunks directly to the LLM. Instead, a Context Builder assembles a structured payload from the top-ranked chunks, recent conversation history, workspace summary, and user query. Internally, I recommend representing this context as JSON because it is machine-friendly, deterministic, and easy to validate. For example, the backend may build a payload containing sections such as system instructions, retrieved sources, conversation memory, and user intent. However, the LLM should ultimately receive a carefully formatted prompt rather than raw JSON because language models reason more effectively over structured natural language. The prompt can be assembled as: System Instructions → Workspace Context → Retrieved Document Evidence → Recent Conversation Context → User Query → Response Rules. This makes the LLM operate on clean, curated information instead of noisy document fragments. Since your architecture is retrieval-first, the LLM's role becomes contextual reasoning and synthesis rather than information discovery, which significantly improves response quality and reduces hallucinations.

For output handling, Markdown is absolutely the best choice for your system. Modern LLMs naturally generate high-quality Markdown, it is human-readable, lightweight, easily rendered in Next.js, and requires far less parsing complexity than HTML or custom rich-text formats. The ideal approach is to instruct the LLM to return responses in a controlled Markdown structure such as headings, bullet lists, numbered steps, code blocks, tables, notes, warnings, and citations. For example, the LLM can return sections like "Summary", "Key Findings", "Technical Details", and "Recommendations" depending on the query type. On the backend, store the raw Markdown response in SQLite exactly as generated. On the frontend, use a Markdown renderer (such as react-markdown) to convert the content into rich UI components. Additionally, create a response parser layer that validates the output before displaying it. This parser can identify malformed Markdown, extract citations, detect code blocks, process tables, and attach source references from retrieved chunks. In practice, the flow becomes: User Query → Retrieval → Prompt Builder → LLM → Markdown Response → Response Validator → Markdown Renderer → User Interface. This architecture gives you structured outputs without forcing the model into rigid JSON schemas, minimizes parsing failures, reduces token consumption, improves readability, and keeps both Groq-hosted models and local Qwen models working consistently. For a document-centric RAG system, Markdown provides the best balance between machine processability, frontend rendering flexibility, and user experience.


## Storage Architecture

The storage architecture is intentionally minimal and optimized for a single-user prototype environment. Uploaded documents are stored within isolated workspace directories. SQLite serves as the primary structured storage system and manages workspace metadata, document metadata, chat history, analytics information, retrieval references, and application state.

FAISS functions as the semantic vector storage engine and stores document embeddings generated during ingestion. BM25 indexes support lexical retrieval operations and complement semantic search during hybrid retrieval. Workspace isolation is enforced through unique workspace identifiers that act as partition keys across all storage components, ensuring complete separation of documents, retrieval indexes, metadata, and conversational history.

This storage architecture provides fast retrieval performance, simplified deployment, reduced operational complexity, and full control over data management while remaining suitable for future scaling requirements.

# Retrieval Configuration Specification

This document acts as the single source of truth for retrieval configuration parameters.

## Chunking Configuration

```text
Chunk Size           : 512 Tokens
Chunk Overlap        : 100 Tokens
Chunk Strategy       : Recursive Text Splitter
Minimum Chunk Size   : 100 Tokens
```

## Embedding Configuration

```text
Model :
sentence-transformers/all-MiniLM-L6-v2

Embedding Dimensions :
384
```

## Retrieval Configuration

```text
FAISS Retrieval Top-K      : 50
BM25 Retrieval Top-K       : 50
```

## RRF Configuration

```text
Input :
50 FAISS Results
50 BM25 Results

RRF Constant :
60

Output :
Top 20 Candidates
```

## Cross Encoder Configuration

```text
Model :
cross-encoder/ms-marco-MiniLM-L-6-v2

Input :
Top 20 RRF Results

Output :
Top 5 Chunks

Minimum Relevance Score :
0.60
```

## Context Compression

```text
Duplicate Suppression :
Enabled

Near Duplicate Threshold :
90%

Final Context Chunks :
3 - 5
```

## Memory Configuration

```text
Recent Chat Window :
Last 5 Messages

Conversation Summary :
Updated Every 10 Messages

Workspace Summary :
Stored in SQLite
```

## LLM Configuration

```text
Simple Mode :
Qwen2.5-3B-Instruct

Medium Mode :
Groq

Expert Mode :
Groq

Fallback :
Qwen2.5-3B-Instruct
```

## Retrieval Confidence Threshold

```text
Cross Encoder Score >= 0.60
AND
At Least 2 Relevant Chunks
```

If conditions fail:

```text
Document Confidence = LOW

Response:
"I could not find sufficient information in uploaded documents."
```


# Database Design

The database architecture follows a hybrid storage model consisting of SQLite for structured data management and FAISS for semantic vector storage. SQLite functions as the primary relational database responsible for maintaining workspace metadata, document metadata, chat history, retrieval references, analytics information, and application state. FAISS stores semantic embeddings generated from uploaded document chunks and enables efficient vector similarity search during retrieval operations. BM25 indexes complement FAISS by providing lexical retrieval capabilities over processed document content.

The Workspace table serves as the root entity of the relational schema and maintains information related to workspace identification, creation metadata, storage statistics, processing metrics, and operational status. Each workspace acts as an isolated namespace and serves as the parent entity for documents, conversations, analytics, and retrieval operations.

The Documents table stores metadata associated with uploaded files, including document identifiers, workspace references, file names, document types, upload timestamps, processing status, chunk statistics, and storage information. A one-to-many relationship exists between workspaces and documents, allowing multiple documents to reside within a single workspace.

The Chunks table maintains references to document chunks generated during ingestion. Each chunk record contains workspace identifiers, document identifiers, chunk identifiers, chunk positions, textual content references, embedding references, and retrieval metadata. Although embeddings are stored within FAISS, chunk metadata remains accessible through SQLite to support retrieval workflows and contextual reconstruction.

The Conversations table stores chat interactions between users and the AI system. Each record contains workspace references, message identifiers, user queries, generated responses, timestamps, model selection information, retrieval references, and contextual metadata. This structure enables conversation persistence, history retrieval, and contextual memory management.

The Analytics table stores workspace usage metrics such as document counts, chunk counts, retrieval activity, storage utilization, processing statistics, query volume, and model usage information. These records support workspace monitoring and analytics visualization within the frontend interface.

At the storage level, all tables are indexed using workspace identifiers to enforce isolation and improve query performance. SQLite utilizes B-Tree indexing internally to provide efficient retrieval of structured records, while FAISS performs approximate nearest neighbor searches over semantic embeddings. Together, these components create a hybrid database architecture that balances relational consistency, retrieval performance, storage efficiency, and implementation simplicity while supporting the retrieval-centric design philosophy of the overall system.

# Database Schema Specification

## Workspace Table

The Workspace table serves as the root entity of the system and acts as the isolation boundary for documents, conversations, retrieval indexes, analytics, and contextual memory.

| Column          | Type         | Description             |
| --------------- | ------------ | ----------------------- |
| workspace_id    | UUID         | Primary Key             |
| workspace_name  | VARCHAR(255) | Workspace Name          |
| description     | TEXT         | Optional Description    |
| created_at      | DATETIME     | Creation Timestamp      |
| updated_at      | DATETIME     | Last Modified Timestamp |
| status          | VARCHAR(20)  | Active / Archived       |
| total_documents | INTEGER      | Number of Documents     |
| total_chunks    | INTEGER      | Number of Chunks        |
| storage_used_mb | FLOAT        | Workspace Storage Usage |

---

## Documents Table

Stores uploaded document metadata.

| Column            | Type         | Description                               |
| ----------------- | ------------ | ----------------------------------------- |
| document_id       | UUID         | Primary Key                               |
| workspace_id      | UUID         | Foreign Key                               |
| file_name         | VARCHAR(255) | Original File Name                        |
| file_type         | VARCHAR(20)  | PDF / DOCX                                |
| file_size_mb      | FLOAT        | File Size                                 |
| upload_time       | DATETIME     | Upload Timestamp                          |
| processing_status | VARCHAR(20)  | Pending / Processing / Completed / Failed |
| total_chunks      | INTEGER      | Generated Chunks                          |
| embedding_status  | BOOLEAN      | Embeddings Generated                      |

---

## Chunks Table

Stores chunk metadata and references.

| Column        | Type         | Description     |
| ------------- | ------------ | --------------- |
| chunk_id      | UUID         | Primary Key     |
| workspace_id  | UUID         | Foreign Key     |
| document_id   | UUID         | Foreign Key     |
| chunk_index   | INTEGER      | Chunk Order     |
| chunk_text    | TEXT         | Chunk Content   |
| embedding_ref | VARCHAR(255) | FAISS Reference |
| token_count   | INTEGER      | Chunk Tokens    |
| created_at    | DATETIME     | Timestamp       |

---

## Conversations Table

Stores workspace-specific chat history.

| Column       | Type         | Description      |
| ------------ | ------------ | ---------------- |
| message_id   | UUID         | Primary Key      |
| workspace_id | UUID         | Foreign Key      |
| role         | VARCHAR(20)  | User / Assistant |
| message      | TEXT         | Message Content  |
| model_used   | VARCHAR(100) | Groq / Qwen      |
| created_at   | DATETIME     | Timestamp        |

---

## Workspace Summary Table

Stores compressed contextual memory.

| Column       | Type     | Description      |
| ------------ | -------- | ---------------- |
| summary_id   | UUID     | Primary Key      |
| workspace_id | UUID     | Foreign Key      |
| summary_text | TEXT     | Context Summary  |
| last_updated | DATETIME | Update Timestamp |

---

## Analytics Table

Stores workspace monitoring data.

| Column               | Type     | Description        |
| -------------------- | -------- | ------------------ |
| analytics_id         | UUID     | Primary Key        |
| workspace_id         | UUID     | Foreign Key        |
| total_queries        | INTEGER  | Queries Processed  |
| total_documents      | INTEGER  | Documents Uploaded |
| total_chunks         | INTEGER  | Chunks Generated   |
| total_storage_mb     | FLOAT    | Storage Usage      |
| groq_requests        | INTEGER  | API Requests       |
| local_model_requests | INTEGER  | Local LLM Usage    |
| last_updated         | DATETIME | Timestamp          |


# Workflow

## Pipeline Workflow

The system operates through five independent yet interconnected pipelines that collectively manage document processing, retrieval, memory management, and response generation. The workflow begins with the Workspace Management Pipeline, where users create isolated workspaces that serve as independent environments for documents, conversations, analytics, and retrieval operations.

When documents are uploaded, the Document Ingestion Pipeline activates and performs text extraction, tokenization, chunk generation, semantic embedding creation, metadata generation, and vector indexing. The resulting embeddings are stored in FAISS while associated metadata is stored within SQLite. This pipeline executes only during document uploads and remains inactive during normal chat interactions.

When a user submits a query, the Information Retrieval Pipeline is triggered. The query undergoes NLP-based preprocessing and reformulation to improve retrieval effectiveness. The reformulated query is simultaneously processed through FAISS semantic retrieval and BM25 lexical retrieval. Retrieved candidates are combined using Reciprocal Rank Fusion and optionally refined using Cross-Encoder reranking. Duplicate suppression and context compression mechanisms remove redundant information before constructing a compact context package.

The Context & Memory Pipeline retrieves recent workspace conversations, summarized historical context, and workspace-specific memory information. Finally, the LLM Generation Pipeline combines retrieved document context, conversation context, system instructions, and user intent to generate an accurate response. The generated answer is stored in chat history and returned to the user.

## FastAPI Server Workflow

The FastAPI server functions as the orchestration layer connecting frontend interactions with backend pipelines. Upon receiving a request, the server validates input parameters, verifies workspace context, performs authorization checks when applicable, and routes the request to the appropriate service.

For document uploads, the server schedules ingestion tasks and monitors processing progress. For chat requests, it coordinates retrieval, memory management, and language model workflows while maintaining structured logs throughout the process. Error handling mechanisms intercept failures such as invalid uploads, retrieval failures, expired API keys, model failures, or storage issues and convert them into user-friendly responses while preserving detailed diagnostic information within backend logs.

The server maintains centralized logging, health monitoring, startup validation, model initialization, and resource management to ensure reliable operation and efficient debugging.
# API Contract

The system follows a Contract-First API Design approach where the API specification acts as the single source of truth between the frontend and backend. Every endpoint, request schema, response structure, validation rule, error format, and authentication requirement is formally defined before implementation. This approach enables parallel frontend and backend development, reduces integration failures, improves maintainability, and ensures predictable communication across the system. OpenAPI specifications generated through FastAPI serve as the primary contract definition mechanism, providing machine-readable and human-readable API documentation simultaneously. FastAPI natively supports OpenAPI generation and schema validation through Pydantic models, making it suitable for strongly typed API contracts.

The API architecture follows RESTful design principles with resource-oriented endpoints such as `/workspace`, `/document`, `/chat`, `/analytics`, and `/system`. Endpoints use standard HTTP methods including GET, POST, PUT, PATCH, and DELETE, while maintaining consistent request and response formats throughout the application. Each API response follows a standardized structure containing status information, response data, metadata, execution details, and error information when applicable. Workspace identifiers remain mandatory across workspace-scoped operations to enforce strict isolation and prevent accidental cross-workspace access. Proper HTTP status codes are returned for successful operations, validation failures, retrieval errors, storage failures, processing issues, and model execution failures. API versioning is incorporated through versioned routes to ensure future compatibility without breaking existing frontend integrations.

All request and response models are represented using dedicated Pydantic schemas rather than direct database entities. This separation prevents contract drift, improves validation consistency, and ensures clear boundaries between storage models and API models. The contract additionally defines response structures for document processing progress, retrieval metadata, reranking statistics, model selection information, workspace analytics, system health status, and fallback execution events. Since the platform contains AI, NLP, IR, and retrieval pipelines, observability fields such as processing duration, retrieval source counts, confidence indicators, and model provider information are included where necessary to improve transparency and debugging capabilities.
# API Endpoint Specification

## Workspace APIs

### Create Workspace

```http
POST /api/v1/workspace
```

Request

```json
{
  "workspace_name": "Research Papers",
  "description": "AI Research Workspace"
}
```

Response

```json
{
  "success": true,
  "workspace_id": "uuid",
  "message": "Workspace created successfully"
}
```

---

### List Workspaces

```http
GET /api/v1/workspace
```

---

### Delete Workspace

```http
DELETE /api/v1/workspace/{workspace_id}
```

---

## Document APIs

### Upload Document

```http
POST /api/v1/document/upload
```

Form Data

```text
workspace_id
file
```

Response

```json
{
  "success": true,
  "document_id": "uuid",
  "status": "processing"
}
```

---

### Processing Status

```http
GET /api/v1/document/status/{document_id}
```

---

## Chat APIs

### Ask Query

```http
POST /api/v1/chat/query
```

Request

```json
{
  "workspace_id": "uuid",
  "query": "Explain Retrieval Augmented Generation",
  "mode": "expert"
}
```

Response

```json
{
  "success": true,
  "response": "Generated Answer",
  "model_used": "groq",
  "retrieval_chunks": 5,
  "processing_time_ms": 1245
}
```

---

### Chat History

```http
GET /api/v1/chat/history/{workspace_id}
```

---

## Analytics APIs

### Workspace Analytics

```http
GET /api/v1/analytics/{workspace_id}
```

---

## System APIs

### Health Check

```http
GET /api/v1/system/health
```

### Model Status

```http
GET /api/v1/system/model-status
```



## User Interface Workflow

The user interface is designed around workspace-centric interactions. Users begin by creating or selecting a workspace before uploading documents relevant to a specific research domain or project. Uploaded documents are processed in the background while progress and system status are communicated through dedicated interface components.

Once processing is complete, users interact with the chatbot through the chat interface. Queries are submitted to the backend, responses are streamed back to the frontend, and relevant workspace context is maintained throughout the conversation. Additional interface modules provide analytics, document management, system status information, and workspace monitoring while maintaining complete isolation between workspaces.

This workflow enables users to focus on information discovery and document exploration without being exposed to underlying system complexity.

# Data Flow

The end-to-end data flow begins when a user uploads one or more documents into a selected workspace. The uploaded documents are transferred from the frontend to the FastAPI server, which forwards them to the Document Ingestion Pipeline. The ingestion subsystem extracts text content, performs tokenization and chunk generation, and creates semantic embeddings using Sentence Transformers. Generated embeddings are stored within FAISS while document metadata, chunk references, workspace information, and processing details are stored within SQLite.

When a user submits a query, the request travels from the Next.js frontend to the FastAPI orchestration layer. The query is first validated and associated with the correct workspace. The NLP module analyzes the query, performs lightweight reformulation when necessary, and generates an optimized retrieval query. The Retrieval Pipeline then performs hybrid retrieval by executing both semantic search against FAISS and lexical search through BM25 indexes. Retrieved candidates are merged using Reciprocal Rank Fusion, reranked through Cross-Encoder evaluation when applicable, and compressed into a final context package.

Simultaneously, the Context & Memory subsystem retrieves recent conversation history and workspace-specific contextual summaries from SQLite. The retrieval context, memory context, user query, and system instructions are combined into a structured prompt and forwarded to the LLM Generation Pipeline. Depending on the selected operating mode, the request is processed either through Groq-hosted language models or the local Qwen2.5-3B-Instruct model.

The generated response is returned to the FastAPI server, stored within workspace chat history, logged for observability purposes, and transmitted back to the frontend. The user interface then updates the conversation view, analytics state, and workspace activity information. Throughout the entire lifecycle, workspace identifiers remain attached to every operation, ensuring complete workspace isolation and preventing data leakage between independent user environments. The resulting architecture creates a retrieval-first, context-aware, and scalable flow that maximizes response quality while minimizing latency, token consumption, and computational overhead.


# System Design Considerations

The system design prioritizes simplicity, maintainability, and performance while remaining flexible enough to accommodate future enhancements. Since the project targets a prototype environment rather than a large-scale production deployment, the architecture intentionally avoids distributed systems, microservices, event-driven architectures, and complex infrastructure components that would introduce unnecessary operational overhead. Instead, a layered architecture combined with pipeline-based workflow segregation is adopted to ensure clear separation of responsibilities and ease of debugging.

Workspace isolation serves as a core design principle throughout the system. Every document, retrieval operation, metadata record, vector embedding, chat history entry, and analytics metric is associated with a unique workspace identifier to prevent data leakage across independent user environments. The backend follows the principle of single responsibility by separating Workspace Management, Document Ingestion, Information Retrieval, Context Management, and LLM Generation into independent pipelines that can evolve without affecting one another.

The system follows retrieval-first design principles where Information Retrieval performs the majority of contextual reasoning before invoking the language model. This reduces hallucination risk, minimizes token consumption, and improves response accuracy. The language model acts as a reasoning and generation layer rather than a primary knowledge source. To improve maintainability, all business logic remains within service layers while storage operations are isolated within repository layers. The frontend follows modular and reusable component architecture, ensuring that user interface functionality remains independent from backend implementation details.

Resource efficiency is another critical consideration due to free-tier development constraints and local deployment requirements. Expensive operations such as embedding generation, reranking, and inference are executed only when necessary. Local language model integration functions as a fallback mechanism rather than a primary dependency, ensuring uninterrupted service while minimizing hardware requirements. Overall, the design emphasizes controlled complexity, modularity, fault tolerance, code reusability, and long-term maintainability.
# Functional Requirements Specification

The system shall provide users with the ability to create, manage, and delete isolated workspaces that serve as independent environments for document storage, retrieval, analytics, and conversational interactions. Each workspace shall maintain complete isolation from all other workspaces, ensuring that documents, vector indexes, chat history, metadata, retrieval operations, and generated responses remain workspace-specific. Users shall be able to upload multiple PDF and DOCX documents into a selected workspace, and the system shall process these documents through an ingestion pipeline consisting of text extraction, chunk generation, embedding creation, metadata generation, and vector indexing.

The system shall support intelligent document retrieval using a hybrid retrieval architecture that combines semantic retrieval through FAISS and lexical retrieval through BM25. User queries shall undergo NLP-based preprocessing and query enhancement before retrieval execution. Retrieved candidates shall be ranked using Reciprocal Rank Fusion and optionally refined using Cross-Encoder reranking to maximize relevance before constructing the final context package. The system shall provide accurate, context-aware responses by utilizing retrieved document information as the primary knowledge source and shall minimize hallucinations through retrieval-grounded response generation.

The system shall maintain workspace-specific conversational context through structured memory management. Recent conversations, contextual summaries, and retrieval history shall be utilized to improve response continuity while preventing unnecessary token consumption. Chat history shall be stored and retrievable for future interactions within the same workspace.

The system shall support multiple AI operating modes, including Simple, Medium, and Expert modes. Medium and Expert modes shall utilize Groq-hosted language models, while Simple mode and fallback operations shall utilize the locally deployed Qwen2.5-3B-Instruct model. If external AI services become unavailable, the system shall automatically switch to the local model to maintain uninterrupted operation.

The system shall provide workspace analytics that display document statistics, storage utilization, retrieval metrics, processing activity, and conversational usage information. Users shall receive clear system feedback during document uploads, ingestion processes, retrieval operations, model execution, and error scenarios. The system shall also provide appropriate fallback responses whenever uploaded documents do not contain sufficient information to answer a query while clearly distinguishing document-based responses from general AI-generated information.
# Non-Functional Requirements

The system shall prioritize maintainability, performance, reliability, and resource efficiency while operating within free-tier development constraints and local deployment environments. The architecture shall follow modular design principles, ensuring clear separation of responsibilities across Workspace Management, Document Ingestion, Information Retrieval, Context Management, and LLM Generation pipelines. All components shall adhere to object-oriented design principles, including high cohesion, low coupling, code reusability, and separation of concerns.

The system shall maintain low response latency by executing computationally expensive operations only when required. Document ingestion, embedding generation, reranking, and language model inference shall be isolated and optimized to reduce unnecessary resource consumption. The retrieval-first architecture shall ensure that only highly relevant information is provided to the language model, reducing token utilization and inference costs.

The system shall provide fault tolerance through centralized error handling, logging, health monitoring, and fallback mechanisms. Failures related to document processing, retrieval operations, storage access, API availability, or language model execution shall be handled gracefully while providing meaningful feedback to both users and developers. Comprehensive logging shall be maintained to support debugging, monitoring, and operational transparency.

The system shall ensure workspace-level data isolation at all stages of processing, storage, retrieval, and response generation. Every operation involving documents, embeddings, metadata, retrieval indexes, and conversations shall be associated with a unique workspace identifier. The architecture shall prevent unauthorized cross-workspace access and eliminate the possibility of workspace contamination.

The system shall support scalability within the constraints of a prototype environment. Storage structures, retrieval indexes, and application workflows shall be designed to accommodate increasing document volumes and conversational history without requiring major architectural changes. The frontend shall remain responsive through efficient state management, selective rendering, lazy loading, and reusable component architecture. The overall solution shall remain lightweight, deployable on commodity hardware, and maintain acceptable performance under expected workload conditions.
# Prompt Engineering Strategy

The system follows a Retrieval-Grounded Prompt Engineering architecture where prompts are dynamically constructed using retrieval context, conversational memory, workspace metadata, system instructions, user intent, and operational mode selection. Rather than relying on static prompts, the architecture builds contextual prompts at runtime after the Information Retrieval Pipeline completes semantic retrieval, lexical retrieval, reranking, duplicate suppression, and context compression. This ensures that the language model receives only highly relevant information and minimizes hallucination risk.

The prompting strategy is organized into multiple layers. The first layer consists of system instructions that define model behavior, workspace boundaries, response formatting rules, hallucination prevention policies, fallback conditions, and source-grounding requirements. The second layer contains workspace context, including workspace summaries, recent conversation history, and relevant contextual memory. The third layer contains retrieval context generated through FAISS, BM25, RRF, and Cross-Encoder reranking. The fourth layer contains the user query and NLP-enhanced reformulated query representation. The final layer contains response constraints such as answer style, reasoning mode, response depth, citation requirements, and operational mode configurations.

The architecture supports adaptive prompting based on query complexity. Simple factual queries utilize lightweight prompts with smaller context windows, while analytical or research-oriented queries receive expanded retrieval context and expert reasoning instructions. Medium and Expert modes leverage larger context windows through Groq-hosted models, while Simple mode and local fallback execution use compressed prompts optimized for Qwen2.5-3B-Instruct. The system additionally incorporates retrieval confidence awareness, allowing prompt behavior to change when retrieval relevance scores fall below predefined thresholds. In such situations, the prompt explicitly instructs the model to acknowledge insufficient document evidence rather than generating unsupported answers.

The overall strategy follows a retrieval-first reasoning model where the language model is treated as a contextual reasoning engine rather than a knowledge retrieval mechanism. Most intelligence originates from retrieval quality, contextual compression, memory management, and ranking systems, allowing smaller models to produce significantly more accurate responses than traditional prompt-only chatbot architectures.

# Retrieval Configuration Specification

This document acts as the single source of truth for retrieval configuration parameters.

## Chunking Configuration

```text
Chunk Size           : 512 Tokens
Chunk Overlap        : 100 Tokens
Chunk Strategy       : Recursive Text Splitter
Minimum Chunk Size   : 100 Tokens
```

## Embedding Configuration

```text
Model :
sentence-transformers/all-MiniLM-L6-v2

Embedding Dimensions :
384
```

## Retrieval Configuration

```text
FAISS Retrieval Top-K      : 50
BM25 Retrieval Top-K       : 50
```

## RRF Configuration

```text
Input :
50 FAISS Results
50 BM25 Results

RRF Constant :
60

Output :
Top 20 Candidates
```

## Cross Encoder Configuration

```text
Model :
cross-encoder/ms-marco-MiniLM-L-6-v2

Input :
Top 20 RRF Results

Output :
Top 5 Chunks

Minimum Relevance Score :
0.60
```

## Context Compression

```text
Duplicate Suppression :
Enabled

Near Duplicate Threshold :
90%

Final Context Chunks :
3 - 5
```

## Memory Configuration

```text
Recent Chat Window :
Last 5 Messages

Conversation Summary :
Updated Every 10 Messages

Workspace Summary :
Stored in SQLite
```

## LLM Configuration

```text
Simple Mode :
Qwen2.5-3B-Instruct

Medium Mode :
Groq

Expert Mode :
Groq

Fallback :
Qwen2.5-3B-Instruct
```

## Retrieval Confidence Threshold

```text
Cross Encoder Score >= 0.60
AND
At Least 2 Relevant Chunks
```

If conditions fail:

```text
Document Confidence = LOW

Response:
"I could not find sufficient information in uploaded documents."
```


# DSA & Optimization Considerations

Data Structures and Algorithms play a significant role in ensuring efficient storage, retrieval, memory management, and overall system responsiveness. The architecture incorporates carefully selected structures to optimize both time complexity and resource utilization while maintaining implementation simplicity.

Hash Maps are used extensively for workspace indexing, state management, metadata lookups, and cache access due to their constant-time lookup characteristics. Workspace identifiers serve as primary keys for isolating documents, retrieval indexes, chat histories, and analytics data. SQLite internally utilizes B-Tree indexing structures that provide efficient querying of structured data such as conversations, document metadata, workspace information, and system logs.

The retrieval subsystem relies on FAISS for approximate nearest neighbor search, enabling highly efficient semantic retrieval from large collections of document embeddings. BM25 provides optimized lexical retrieval capabilities for exact keyword matching and domain-specific terminology. Reciprocal Rank Fusion combines the strengths of both retrieval strategies without requiring score normalization, while Cross-Encoder reranking improves precision by performing deep query-document relevance evaluation on a limited candidate set. This multi-stage retrieval architecture balances retrieval quality and computational efficiency.

For conversation management, deque-based sliding windows maintain recent conversational context with efficient insertion and removal operations. Conversation summarization reduces memory growth by compressing older interactions into concise contextual representations. Priority queues are implicitly utilized during ranking and candidate selection processes, while retrieval candidate pruning minimizes unnecessary processing. Duplicate suppression and context compression reduce token utilization before LLM invocation, improving response speed and lowering computational costs.

The system follows a retrieval-first optimization strategy where relevance filtering occurs before language model processing. This ensures that expensive inference operations receive only high-quality contextual information, maximizing output quality while minimizing latency, memory usage, and resource consumption.
# Limitations & Trade-Offs

Although the proposed architecture provides strong retrieval capabilities, contextual awareness, and modular system design, several limitations and trade-offs must be acknowledged. These decisions are intentional and align with the project's objective of maintaining simplicity, cost efficiency, and manageable development complexity.

The system utilizes SQLite as its primary structured storage mechanism due to its simplicity and lightweight deployment characteristics. While suitable for prototype and single-user environments, SQLite may become a bottleneck under high concurrency scenarios or large-scale multi-user deployments. Similarly, FAISS provides efficient vector retrieval but lacks some advanced operational features available in specialized vector database platforms.

The use of a local fallback language model introduces a trade-off between availability and response quality. While Qwen2.5-3B-Instruct ensures continued operation when external APIs are unavailable, its reasoning capabilities, contextual understanding, and response quality may not match larger cloud-hosted models. Additionally, local inference remains constrained by available system resources, particularly memory and processing power.

The retrieval pipeline incorporates BM25, FAISS, RRF, and Cross-Encoder reranking to maximize relevance. Although this significantly improves retrieval quality, it introduces additional processing overhead compared to simpler retrieval approaches. To mitigate latency, reranking is performed only on a limited candidate set rather than the entire retrieval result pool.

Another intentional trade-off involves context management. Instead of implementing a fully persistent graph database or enterprise-scale memory architecture, the system uses lightweight contextual memory mechanisms based on chat history, summaries, and workspace-specific metadata. While this approach simplifies implementation and reduces resource consumption, it may provide less sophisticated long-term reasoning compared to dedicated knowledge graph solutions.

The architecture prioritizes maintainability and controlled complexity over maximum scalability. As a result, several advanced capabilities such as distributed processing, horizontal scaling, event-driven communication, real-time synchronization, and large-scale multi-tenant infrastructure are intentionally excluded. These limitations are acceptable within the scope of the project because the primary objective is to build a reliable, explainable, and retrieval-centric AI system that demonstrates strong engineering practices without introducing unnecessary architectural complexity.
# Tech Stack

The proposed system utilizes a carefully selected technology stack that balances performance, maintainability, development simplicity, and resource efficiency while remaining suitable for a retrieval-centric AI architecture. The frontend is developed using Next.js, providing server-side rendering capabilities, efficient routing, component-based architecture, optimized asset loading, and excellent developer productivity. The user interface follows a Bento Grid design system and modular component architecture, enabling reusable UI components, workspace-based interactions, analytics visualization, document management, and conversational interfaces. State management is implemented using lightweight client-side state containers to maintain workspace state, chat state, document state, analytics state, and system status while minimizing unnecessary component re-rendering.

The backend is implemented using FastAPI, which serves as the orchestration layer connecting all backend pipelines. FastAPI was selected due to its asynchronous capabilities, automatic API documentation generation, strong type validation through Pydantic, high performance, and seamless integration with modern Python AI ecosystems. The backend follows a layered architecture consisting of API Layer, Service Layer, Repository Layer, and Storage Layer to ensure separation of concerns and maintainable code organization. Python serves as the primary programming language due to its extensive ecosystem support for Natural Language Processing, Information Retrieval, Machine Learning, and AI model integration.

For storage, SQLite functions as the primary structured database responsible for workspace metadata, document metadata, chat history, analytics information, retrieval references, and application state. SQLite provides ACID compliance, lightweight deployment, simplified backup management, and efficient querying capabilities suitable for a prototype environment. Semantic vector storage is handled using FAISS, which enables efficient similarity search and approximate nearest neighbor retrieval over document embeddings. BM25 indexing supports lexical retrieval operations and complements semantic retrieval through hybrid search mechanisms. Sentence Transformers are used for embedding generation, converting textual document chunks into dense vector representations suitable for semantic retrieval.

The AI infrastructure combines cloud-hosted and local language model execution. Groq APIs provide high-performance inference for medium and expert reasoning modes, while Qwen2.5-3B-Instruct serves as a local fallback model to ensure uninterrupted operation when external services are unavailable. The overall stack emphasizes retrieval-first architecture, modularity, low operational overhead, simplified deployment, and efficient resource utilization while maintaining strong response quality and contextual awareness.
# Models

## Natural Language Processing (NLP) Models

The NLP subsystem functions as the preprocessing and query enhancement layer of the system. Its primary responsibility is to improve retrieval effectiveness before information reaches the retrieval engine. The NLP pipeline performs query analysis, spelling correction, token normalization, stop-word filtering where appropriate, semantic intent understanding, query expansion, and lightweight query reformulation. Rather than relying solely on user-provided text, the system attempts to identify the actual information requirement behind the query and generate an optimized representation suitable for retrieval.

Sentence Transformer models are utilized for semantic representation learning and embedding generation. During document ingestion, textual chunks extracted from uploaded documents are converted into dense semantic vectors. During query execution, user queries are transformed into the same embedding space, enabling semantic similarity matching between queries and stored document content. This approach allows the system to retrieve relevant information even when exact keywords are not present within uploaded documents.

The NLP subsystem is intentionally designed to support retrieval rather than answer generation. Its primary objective is to maximize retrieval relevance, improve search accuracy, and reduce ambiguity before information enters the Information Retrieval pipeline.

## Information Retrieval (IR) Models

The Information Retrieval subsystem serves as the primary intelligence layer of the architecture and is responsible for identifying the most relevant information from uploaded documents. The retrieval process follows a hybrid retrieval strategy combining semantic retrieval and lexical retrieval techniques to maximize recall and precision.

FAISS functions as the semantic retrieval engine. It performs approximate nearest neighbor searches over document embeddings generated during ingestion. Semantic retrieval enables the system to identify conceptually related information even when user queries differ from the exact wording found within uploaded documents.

BM25 functions as the lexical retrieval engine. Unlike semantic retrieval, BM25 focuses on keyword relevance, exact term matching, domain-specific terminology, acronyms, technical phrases, and rare entities. This ensures that highly specific document content is not overlooked during retrieval.

The outputs from FAISS and BM25 are merged using Reciprocal Rank Fusion (RRF). RRF combines ranking positions from multiple retrieval systems rather than relying on retrieval scores directly. This technique provides a balanced retrieval strategy by leveraging the strengths of both semantic and lexical retrieval methods.

To further improve precision, Cross-Encoder reranking is applied to a limited set of top-ranked candidates. Unlike embedding-based retrieval models, the Cross-Encoder evaluates the user query and candidate chunks simultaneously, allowing deeper contextual understanding and more accurate relevance estimation. Duplicate suppression and context compression mechanisms are then applied before constructing the final context package for the language model.

## Large Language Models (LLM)

The LLM subsystem acts as the final reasoning and response generation layer. Unlike conventional chatbot architectures where the language model serves as the primary intelligence source, the proposed system follows a retrieval-first design philosophy. Most contextual understanding and information discovery occur within the retrieval pipeline before the language model is invoked.

The primary inference provider is `Groq-hosted language models`, which are utilized for Medium and Expert operating modes. Groq models provide fast inference, large context windows, improved reasoning capabilities, and enhanced response quality. These models receive curated context generated by the retrieval subsystem and focus on synthesizing information, generating coherent responses, and maintaining conversational flow.

To ensure system availability and reduce dependency on external APIs, `Qwen2.5-3B-Instruct` is integrated as a local fallback language model. The local model supports Simple mode operation and serves as an alternative inference engine whenever external services become unavailable. Although smaller than cloud-hosted alternatives, `Qwen2.5-3B-Instruct` provides a strong balance between response quality, resource consumption, retrieval-grounded answering, and local deployment feasibility.

The language model layer receives a structured prompt containing the user query, retrieved document chunks, conversation context, workspace-specific memory, and system instructions. Because retrieval quality is prioritized throughout the architecture, the language model focuses primarily on reasoning, summarization, explanation, and response generation rather than knowledge retrieval. This significantly reduces hallucination risk, improves answer accuracy, and maximizes utilization of uploaded document content.
# Failover and Fallback Mechanism

The system incorporates a multi-layer failover and fallback architecture designed to ensure continuous operation even when individual subsystems experience failures. Since the platform combines NLP pipelines, retrieval systems, vector storage, external AI providers, local inference engines, and workspace-specific memory management, fault tolerance is treated as a core architectural requirement rather than an optional enhancement.

At the language model layer, Groq-hosted models act as the primary inference providers for Medium and Expert modes. If Groq API requests fail due to expired API keys, rate limits, network interruptions, service unavailability, authentication failures, or unexpected provider errors, the system automatically activates the local Qwen2.5-3B-Instruct model. This transition occurs without interrupting user workflows, ensuring uninterrupted conversational capabilities. Users receive transparent notifications indicating that fallback execution has occurred while backend logs record detailed diagnostic information for debugging and monitoring purposes.

The retrieval subsystem includes retrieval-level fallback mechanisms. If Cross-Encoder reranking becomes unavailable, the system continues execution using RRF-ranked results. If BM25 retrieval fails, semantic retrieval through FAISS remains active. Similarly, if semantic retrieval becomes unavailable, lexical retrieval continues functioning independently. This layered retrieval strategy ensures graceful degradation rather than complete system failure.

At the memory layer, if contextual summarization fails, the system falls back to recent conversation windows stored within SQLite. If advanced memory retrieval encounters errors, basic workspace chat history remains available. Storage-layer failures are isolated through repository abstraction, allowing service layers to detect and respond to storage exceptions without affecting unrelated system components.

The FastAPI orchestration layer contains centralized exception handling, structured logging, health monitoring, startup validation, and service availability checks. Every critical operation generates observable execution traces containing request identifiers, workspace identifiers, processing durations, retrieval statistics, model execution details, and error information. User-facing failures are converted into understandable messages, while internal logs preserve technical diagnostics for debugging.

The overall failover strategy follows graceful degradation principles. Rather than maximizing feature availability through complex distributed architectures, the system prioritizes maintaining core functionality under degraded conditions. This approach aligns with the project's objective of minimizing architectural complexity while maximizing reliability, explainability, maintainability, and uninterrupted user experience.

# Folder Structure

```text
project-root/
│
├── frontend/
│   │
│   ├── app/
│   │
│   ├── components/
│   │   ├── workspace/
│   │   ├── upload/
│   │   ├── chat/
│   │   ├── analytics/
│   │   └── shared/
│   │
│   ├── services/
│   │
│   ├── store/
│   │
│   ├── hooks/
│   │
│   ├── models/
│   │
│   ├── utils/
│   │
│   ├── constants/
│   │
│   └── styles/ 
│       |── theme/ # centralized color control by material theme
│
│
├── backend/
│   │
│   ├── api/
│   │   ├── workspace/
│   │   ├── document/
│   │   ├── chat/
│   │   ├── analytics/
│   │   └── system/
│   │
│   ├── services/
│   │   ├── workspace/
│   │   ├── document/
│   │   ├── retrieval/
│   │   ├── memory/
│   │   ├── llm/
│   │   └── analytics/
│   │
│   ├── repositories/
│   │   ├── sqlite/
│   │   ├── vector/
│   │   └── bm25/
│   │
│   ├── providers/
│   │   ├── embeddings/
│   │   ├── groq/
│   │   └── qwen/
│   │
│   ├── schemas/
│   │
│   ├── models/
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── logging/
│   │   ├── exceptions/
│   │   └── startup/
│   │
│   ├── utils/
│   │
│   ├── tests/
│   │
│   └── logs/
│
│
├── storage/
│   │
│   ├── uploads/
│   │   └── workspaces/
│   │
│   ├── sqlite/
│   │
│   ├── vectors/
│   │   └── faiss/
│   │
│   ├── bm25/
│   │
│   ├── cache/
│   │
│   └── exports/
│
│
├── secrets/
│   │
│   ├── .env
│   │
│   └── templates/
│
│
└── docs/
```

Why this version is better:

* Only **4 top-level engineering folders**:

  * `frontend`
  * `backend`
  * `storage`
  * `secrets`

* Directly maps to your implementation phases:

  * Workspace Management
  * Document Processing
  * Retrieval
  * Memory
  * LLM
  * Analytics

* Removes the extra `pipelines/` layer because orchestration can live inside Services for the MVP.

* Keeps all persistent data completely outside application code:

  * SQLite DB
  * FAISS indexes
  * BM25 indexes
  * Uploaded documents
  * Cached artifacts

* `secrets/.env` becomes the single location for:

  * Groq API Key
  * HuggingFace Token
  * Model Configuration
  * Retrieval Configuration Overrides
  * Debug Flags

Example:

```env
GROQ_API_KEY=
HF_TOKEN=

ENABLE_BM25=true
ENABLE_RRF=true
ENABLE_CROSS_ENCODER=true
ENABLE_LOCAL_MODEL=true

LOG_LEVEL=INFO
```

* Easier deployment:

```text
frontend/
backend/
storage/
secrets/
```

Everything important lives inside these four folders, which makes backup, debugging, local deployment, and future Dockerization significantly easier.

This structure is lean, maps directly to your architecture decisions, and is unlikely to require major refactoring during development. It also keeps the codebase aligned with the phased implementation plan we've defined. Based on the current design, this would be my final recommended hierarchy. It remains consistent with the earlier architecture while reducing unnecessary nesting and complexity. 
