# RAG Document Intelligence Platform — Frontend Implementation Plan

> **Scope:** Frontend only (Next.js + TypeScript) — Phases 45 through 56.
> The entire backend (FastAPI, SQLite, FAISS, BM25, Groq, Qwen) is complete and operational.
> All endpoints are validated via Swagger. Build and test the UI against the live backend.
>
> **Aesthetic Direction:** Refined industrial minimalism. A purposeful research tool, not a consumer app.
> Dense information layouts, precise typography, controlled motion, bento-grid spatial composition.
> Think: a Bloomberg terminal crossed with a clean academic dashboard. Every pixel earns its place.
>
> **Goal:** Zero bugs, zero flaws, pixel-perfect implementation with seamless backend integration.

---

## How to Read This Plan

Each phase has a clear **Objective** stating what must exist after the phase is complete, a **Technical Context** section explaining the *why* behind every decision, an ordered list of **Micro-Tasks** with enough specificity for the agent to write correct code on the first attempt, and a **Checklist** for verification. Phases build linearly — never skip one. After completing every phase, run the full error verification steps before marking checklist items done.

The agent must treat `tokens.css` as the absolute design contract. Every color, spacing, elevation, and motion token already defined there must be imported and used. No hardcoded hex values, no inline Tailwind colors that bypass the token system.

---

## Pre-Implementation Setup

Before writing a single component, the agent must initialize the project structure and configure all foundational tooling. This scaffolding step is not optional — getting it wrong here causes cascading failures across all subsequent phases.

### Directory Tree to Initialize

Create the following structure inside `frontend/`. Every directory must exist before Phase 45 begins. The reasoning for each folder is explained in-line so the agent understands the intent, not just the location.

```
frontend/
├── app/                          # Next.js App Router root
│   ├── layout.tsx                # Root layout: theme provider, fonts, global CSS
│   ├── page.tsx                  # Root redirect → /workspaces
│   ├── workspaces/
│   │   ├── page.tsx              # Workspace dashboard (bento grid of workspace cards)
│   │   └── [workspaceId]/
│   │       ├── layout.tsx        # Workspace shell: sidebar + tab navigation
│   │       ├── page.tsx          # Default redirect → /chat
│   │       ├── chat/
│   │       │   └── page.tsx      # Chat interface
│   │       ├── documents/
│   │       │   └── page.tsx      # Document manager
│   │       └── analytics/
│   │           └── page.tsx      # Analytics dashboard
│   └── system/
│       └── page.tsx              # System health monitor
├── components/
│   ├── workspace/                # Workspace-specific components
│   │   ├── WorkspaceCard.tsx
│   │   ├── WorkspaceGrid.tsx
│   │   ├── CreateWorkspaceModal.tsx
│   │   └── WorkspaceDeleteDialog.tsx
│   ├── chat/                     # Chat interface components
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── ChatInput.tsx
│   │   ├── ModeSelector.tsx
│   │   ├── SourceCitationPanel.tsx
│   │   └── EmptyConversation.tsx
│   ├── documents/                # Document management components
│   │   ├── DropZone.tsx
│   │   ├── DocumentTable.tsx
│   │   ├── DocumentRow.tsx
│   │   ├── ProcessingStatus.tsx
│   │   └── DocumentDeleteDialog.tsx
│   ├── analytics/                # Analytics visualization components
│   │   ├── AnalyticsBento.tsx
│   │   ├── StatCard.tsx
│   │   ├── ModelUsageChart.tsx
│   │   └── StorageBar.tsx
│   ├── system/                   # System health components
│   │   ├── HealthGrid.tsx
│   │   └── SubsystemCard.tsx
│   ├── layout/                   # Structural layout components
│   │   ├── Sidebar.tsx
│   │   ├── TabNav.tsx
│   │   ├── TopBar.tsx
│   │   └── ThemeToggle.tsx
│   └── shared/                   # Reusable primitives used everywhere
│       ├── Button.tsx
│       ├── Badge.tsx
│       ├── Modal.tsx
│       ├── Spinner.tsx
│       ├── Tooltip.tsx
│       ├── EmptyState.tsx
│       ├── ErrorBoundary.tsx
│       └── MarkdownRenderer.tsx
├── hooks/                        # Custom React hooks
│   ├── useWorkspaces.ts
│   ├── useWorkspace.ts
│   ├── useDocuments.ts
│   ├── useChat.ts
│   ├── useAnalytics.ts
│   ├── useSystemHealth.ts
│   └── usePolling.ts
├── services/                     # Backend API communication layer
│   ├── api.ts                    # Base fetch client with error handling
│   ├── workspace.service.ts
│   ├── document.service.ts
│   ├── chat.service.ts
│   ├── analytics.service.ts
│   └── system.service.ts
├── store/                        # Zustand global state
│   ├── workspace.store.ts
│   ├── chat.store.ts
│   ├── document.store.ts
│   └── ui.store.ts
├── models/                       # TypeScript type definitions (mirrors backend schemas)
│   ├── workspace.model.ts
│   ├── document.model.ts
│   ├── chat.model.ts
│   ├── analytics.model.ts
│   └── system.model.ts
├── utils/
│   ├── cn.ts                     # Class name utility (clsx + twMerge)
│   ├── format.ts                 # Date, file size, number formatters
│   └── constants.ts              # API base URL, query modes, polling intervals
├── styles/
│   ├── globals.css               # imports tokens.css + global resets
│   ├── tokens.css                # Copy of the project-level tokens.css
│   └── typography.css            # Font-face declarations and scale utilities
└── public/
    └── fonts/                    # Self-hosted font files
```

### Technology Stack — Exact Versions

Install the following. Pin these exact versions. Explain to the agent the purpose of each package so substitutions are never made out of confusion.

```
next@14.2.0                    # App Router, Server Components, built-in image/font optimization
react@18.3.0
react-dom@18.3.0
typescript@5.4.0
tailwindcss@3.4.0              # Utility-first CSS — used only for layout helpers; colors come from tokens
postcss@8.4.0
autoprefixer@10.4.0
zustand@4.5.0                  # Minimal global state; no boilerplate, no reducers
react-markdown@9.0.0           # Renders LLM Markdown output safely
remark-gfm@4.0.0               # GitHub-flavored Markdown tables, checkboxes, strikethrough
rehype-highlight@7.0.0         # Code block syntax highlighting in Markdown responses
react-dropzone@14.2.0          # Drag-and-drop file upload with file type validation
framer-motion@11.0.0           # Production-grade animation library for React
recharts@2.12.0                # Lightweight chart library for analytics dashboard
clsx@2.1.0                     # Conditional class merging utility
tailwind-merge@2.2.0           # Merges Tailwind classes intelligently avoiding conflicts
lucide-react@0.378.0           # Consistent, minimal icon set aligned with the aesthetic
```

Do **not** install: Redux, React Query, Axios, styled-components, Emotion, MUI, Chakra, shadcn/ui, or any other UI component library. All components are hand-built to maintain full visual control and keep bundle size minimal.

### Environment Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=DocIntel
NEXT_PUBLIC_POLLING_INTERVAL_MS=2000
```

Create `frontend/.env.example` with the same keys but empty values. This is version-controlled; `.env.local` is not.

### Tailwind Configuration

In `tailwind.config.ts`, the agent must configure Tailwind to recognize and not purge any CSS variable references. Set `content` to scan all `.tsx` and `.ts` files. Do **not** extend the color palette with token values — that would create a parallel color system. Instead, Tailwind is used purely for spacing utilities (`p-4`, `gap-6`, `grid`, `flex`) while all color values are applied via CSS variable references in component-level class names or `style` props.

Add a `borderRadius` extension that maps `standard`, `large`, and `sharp` names to the CSS variables so border radius tokens are accessible as Tailwind classes: `rounded-standard`, `rounded-large`, `rounded-sharp`.

---

## Phase 45 — Next.js Foundation: Routing, Theme Provider, Typography

**Objective:** A booting Next.js application with working dark/light theme switching, correct font loading, global CSS token injection, and a root layout that all subsequent pages inherit from.

**Technical Context:**

The theme system is the deepest dependency of the entire frontend. Every component depends on it. Getting it right here — once — prevents cascading visual bugs later. The chosen approach is: `data-theme` attribute on the `<html>` element, exactly matching the `[data-theme="dark"]` and `[data-theme="light"]` selectors already defined in `tokens.css`. This means no theme-specific CSS classes anywhere in components — all theme-switching is handled by flipping one attribute.

The theme provider is a Client Component (`"use client"`) because it reads from `localStorage`. It wraps the entire application inside the Root Layout and is the only component that touches theme persistence. All other components are Server Components by default (Next.js 14 App Router default).

**Typography choice:** Use `Geist` (Vercel's variable font, available via `next/font/google`) as the monospaced font for code and data values, and `DM Sans` as the body/UI font. DM Sans is geometric, neutral, and highly legible at small sizes — ideal for a research tool. Avoid Inter. Load both via `next/font/google` in the root layout for zero CLS (Cumulative Layout Shift) because Next.js inlines the critical font CSS at build time.

**Micro-Tasks:**

**Task 45.1 — Copy and register `tokens.css`**

Copy the project-level `tokens.css` into `frontend/styles/tokens.css` verbatim. Do not modify it. In `frontend/styles/globals.css`, add `@import './tokens.css';` as the very first line. Then add a global reset after: `*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }`. Set `html` and `body` to `height: 100%` and `background-color: var(--md-sys-color-background)` and `color: var(--md-sys-color-on-background)`. Apply `font-family` to `body` from the DM Sans CSS variable that Next.js will inject.

Set the default `data-theme` on the `<html>` tag to `"dark"` in the root layout. The ThemeProvider will override this on the client immediately after hydration, preventing any flash.

**Task 45.2 — Build the `ThemeProvider` component**

Create `components/layout/ThemeProvider.tsx` as a Client Component. It uses `useState` initialized from `localStorage.getItem('theme') ?? 'dark'`. On mount (inside `useEffect`), it applies `document.documentElement.setAttribute('data-theme', theme)`. It exposes a `toggleTheme` function and the current `theme` value via React Context. Define and export `ThemeContext` and a `useTheme()` hook. The provider wraps `{children}` in a single `<>` fragment — it does not add DOM elements.

Store the context in `store/ui.store.ts` alongside other UI state rather than creating a standalone context file. This keeps all UI-level ephemeral state centralized.

**Task 45.3 — Build the Root Layout**

In `app/layout.tsx`, this is a Server Component. Import `DM_Sans` and `Geist_Mono` from `next/font/google`. Configure `DM_Sans` with subsets `['latin']`, `display: 'swap'`, and `variable: '--font-sans'`. Configure `Geist_Mono` with `variable: '--font-mono'`. Apply both font variables to the `<html>` element's `className`. Set `lang="en"` and the default `data-theme="dark"` on `<html>`. Wrap children with `ThemeProvider`. Import `globals.css`. The `<body>` element receives the font class names.

Define the `metadata` export with `title: 'DocIntel — Document Intelligence Platform'` and a concise description.

**Task 45.4 — Build the root `page.tsx` redirect**

`app/page.tsx` uses Next.js `redirect('/workspaces')` imported from `next/navigation`. It is a Server Component with no JSX. The redirect happens server-side so there is no client-side flash.

**Task 45.5 — Build the `cn()` utility**

In `utils/cn.ts`, export `cn` as: `import { clsx, type ClassValue } from 'clsx'; import { twMerge } from 'tailwind-merge'; export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }`. This utility is used in every component to merge Tailwind utility classes with conditional logic without class conflicts.

**Task 45.6 — Build the `ThemeToggle` component**

In `components/layout/ThemeToggle.tsx`, create a Client Component that calls `useTheme()` and renders a button. When `theme === 'dark'`, show a `Sun` icon (Lucide); when `theme === 'light'`, show a `Moon` icon. Apply `onClick={toggleTheme}`. Style the button using CSS variables: `background: var(--color-bg-input)`, `border: 1px solid var(--color-border)`, `color: var(--color-text-primary)`. Use `border-radius: var(--radius-standard)`. Add a `transition` that inherits from the global `* { transition: ... }` rule in tokens.css.

**Error Verification — Phase 45:**

Run `npm run dev`. The browser must show a blank dark background at `localhost:3000` and redirect to `/workspaces`. No 404. Open DevTools → Elements: `<html data-theme="dark">` must be present. Toggle the theme button (once the TopBar is built in Phase 47, add a temporary toggle button directly to root layout for testing). Verify `localStorage` stores the theme key. Verify no hydration mismatch warnings in the console — they indicate a server/client state divergence in theme initialization.

**Phase 45 Checklist:**
- [x] `tokens.css` is imported globally and CSS variables resolve in DevTools
- [x] `<html data-theme="dark">` is present on initial load
- [x] Theme persists across page refreshes via `localStorage`
- [x] No hydration mismatch warnings in the console
- [x] `DM_Sans` and `Geist_Mono` fonts load with zero layout shift
- [x] Root redirect `/` → `/workspaces` works server-side
- [x] `cn()` utility is importable and merges classes correctly

---

## Phase 46 — Core API Service Layer: Typed Communication with the Backend

**Objective:** A complete, strongly-typed API service layer that abstracts all HTTP communication with the FastAPI backend, handles errors uniformly, and provides each domain service (workspace, document, chat, analytics, system) as importable typed functions.

**Technical Context:**

The API layer is the most critical integration point. Its design determines whether backend errors surface gracefully to users or crash the UI silently. The pattern: a single `api.ts` base client that handles authentication headers, base URL injection, response parsing, and error normalization — then five thin domain service files that call the base client with typed request/response shapes.

The base client uses native `fetch` (no Axios). The reason is: Next.js 14 extends `fetch` natively with caching and revalidation semantics. Using Axios would bypass these optimizations. The base client defines one generic function `apiFetch<T>(path, options) → Promise<T>` that prepends `NEXT_PUBLIC_API_URL`, sets `Content-Type: application/json` on non-FormData requests, and on non-2xx responses, attempts to parse the backend's error JSON `{"success": false, "error": "...", "detail": "..."}` and throws a typed `ApiError` class.

Define `ApiError` as a class that extends `Error` with fields: `statusCode: number`, `errorType: string`, `detail: string`. All service functions catch errors and re-throw as `ApiError`. This means every UI component that calls a service function knows exactly what shape the error is.

**Models First:** Define all TypeScript types in `models/` before writing a single service function. Mirror the backend's Pydantic response schemas exactly. This prevents type drift.

**Micro-Tasks:**

**Task 46.1 — Define all TypeScript models**

In `models/workspace.model.ts`:
```typescript
export interface Workspace {
  workspace_id: string;
  workspace_name: string;
  description: string;
  created_at: string;         // ISO 8601 string from backend
  updated_at: string;
  status: 'active' | 'archived';
  total_documents: number;
  total_chunks: number;
  storage_used_mb: number;
}
export interface CreateWorkspacePayload {
  workspace_name: string;
  description?: string;
}
export interface WorkspaceListResponse {
  workspaces: Workspace[];
  count: number;
}
```

In `models/document.model.ts`:
```typescript
export type ProcessingStatus = 'pending' | 'processing' | 'chunks_ready' | 'completed' | 'failed';
export interface Document {
  document_id: string;
  workspace_id: string;
  file_name: string;
  file_type: 'pdf' | 'docx';
  file_size_mb: number;
  upload_time: string;
  processing_status: ProcessingStatus;
  total_chunks: number;
  embedding_status: boolean;
}
export interface DocumentUploadResponse {
  success: boolean;
  document_id: string;
  status: string;
  message: string;
}
export interface DocumentListResponse {
  documents: Document[];
  count: number;
}
```

In `models/chat.model.ts`:
```typescript
export type ChatMode = 'simple' | 'medium' | 'expert';
export interface Message {
  message_id: string;
  workspace_id: string;
  role: 'user' | 'assistant';
  message: string;
  model_used?: string;
  created_at: string;
  retrieval_chunks: number;
}
export interface QueryPayload {
  workspace_id: string;
  query: string;
  mode: ChatMode;
}
export interface QueryResponse {
  success: boolean;
  response: string;
  model_used: string;
  retrieval_chunks: number;
  processing_time_ms: number;
}
export interface ChatHistoryResponse {
  messages: Message[];
  count: number;
}
```

In `models/analytics.model.ts`:
```typescript
export interface Analytics {
  analytics_id: string;
  workspace_id: string;
  total_queries: number;
  total_documents: number;
  total_chunks: number;
  total_storage_mb: number;
  groq_requests: number;
  local_model_requests: number;
  last_updated: string;
}
```

In `models/system.model.ts`:
```typescript
export type SubsystemStatus = 'ok' | 'error' | 'degraded';
export interface SubsystemCheck {
  status: SubsystemStatus;
  detail?: string;
}
export interface HealthResponse {
  overall: SubsystemStatus;
  database: SubsystemCheck;
  embedding_model: SubsystemCheck;
  groq: SubsystemCheck;
  qwen: SubsystemCheck;
}
export interface ModelStatusResponse {
  groq: SubsystemCheck;
  qwen: SubsystemCheck;
}
```

**Task 46.2 — Build the base API client**

In `services/api.ts`, define:

```typescript
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public errorType: string,
    public detail: string
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  
  // Do not set Content-Type for FormData — browser sets it with boundary automatically
  const isFormData = options.body instanceof FormData;
  const headers: HeadersInit = isFormData
    ? {}
    : { 'Content-Type': 'application/json', ...options.headers };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorType = 'UnknownError';
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      errorType = body.error ?? errorType;
      detail = body.detail ?? detail;
    } catch { /* ignore parse failure */ }
    throw new ApiError(response.status, errorType, detail);
  }

  // Handle 204 No Content (workspace/document deletion)
  if (response.status === 204) return undefined as T;

  return response.json() as Promise<T>;
}
```

The key insight here: `FormData` bodies must not have `Content-Type` set manually. The browser automatically appends the multipart boundary to the content type. Setting it manually breaks file uploads.

**Task 46.3 — Build the workspace service**

In `services/workspace.service.ts`:

```typescript
import { apiFetch } from './api';
import type { Workspace, CreateWorkspacePayload, WorkspaceListResponse } from '../models/workspace.model';

const BASE = '/api/v1/workspace';

export const workspaceService = {
  list: () => apiFetch<WorkspaceListResponse>(BASE),
  
  get: (workspaceId: string) =>
    apiFetch<Workspace>(`${BASE}/${workspaceId}`),
  
  create: (payload: CreateWorkspacePayload) =>
    apiFetch<Workspace>(BASE, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  
  delete: (workspaceId: string) =>
    apiFetch<void>(`${BASE}/${workspaceId}`, { method: 'DELETE' }),
};
```

**Task 46.4 — Build the document service**

In `services/document.service.ts`. The `upload` function uses `FormData` and `multipart/form-data`. The `pollStatus` function is called repeatedly by the polling hook.

```typescript
import { apiFetch } from './api';
import type { DocumentUploadResponse, DocumentListResponse, Document } from '../models/document.model';

const BASE = '/api/v1/document';

export const documentService = {
  upload: (workspaceId: string, file: File) => {
    const form = new FormData();
    form.append('workspace_id', workspaceId);
    form.append('file', file);
    return apiFetch<DocumentUploadResponse>(`${BASE}/upload`, {
      method: 'POST',
      body: form,
    });
  },
  
  getStatus: (documentId: string) =>
    apiFetch<Document>(`${BASE}/status/${documentId}`),
  
  listByWorkspace: (workspaceId: string) =>
    apiFetch<DocumentListResponse>(`${BASE}/workspace/${workspaceId}`),
};
```

**Task 46.5 — Build the chat service**

In `services/chat.service.ts`:

```typescript
import { apiFetch } from './api';
import type { QueryPayload, QueryResponse, ChatHistoryResponse } from '../models/chat.model';

const BASE = '/api/v1/chat';

export const chatService = {
  query: (payload: QueryPayload) =>
    apiFetch<QueryResponse>(`${BASE}/query`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  
  getHistory: (workspaceId: string) =>
    apiFetch<ChatHistoryResponse>(`${BASE}/history/${workspaceId}`),
};
```

**Task 46.6 — Build the analytics and system services**

In `services/analytics.service.ts`:
```typescript
import { apiFetch } from './api';
import type { Analytics } from '../models/analytics.model';

export const analyticsService = {
  get: (workspaceId: string) =>
    apiFetch<Analytics>(`/api/v1/analytics/${workspaceId}`),
};
```

In `services/system.service.ts`:
```typescript
import { apiFetch } from './api';
import type { HealthResponse, ModelStatusResponse } from '../models/system.model';

export const systemService = {
  health: () => apiFetch<HealthResponse>('/api/v1/system/health'),
  modelStatus: () => apiFetch<ModelStatusResponse>('/api/v1/system/model-status'),
};
```

**Task 46.7 — Define all application constants**

In `utils/constants.ts`:
```typescript
export const POLLING_INTERVAL_MS =
  parseInt(process.env.NEXT_PUBLIC_POLLING_INTERVAL_MS ?? '2000', 10);

export const CHAT_MODES = [
  { value: 'simple' as const, label: 'Simple', description: 'Fast, local model' },
  { value: 'medium' as const, label: 'Medium', description: 'Balanced via Groq' },
  { value: 'expert' as const, label: 'Expert', description: 'Deep analysis via Groq' },
] as const;

export const MAX_FILE_SIZE_MB = 50;
export const ACCEPTED_FILE_TYPES = { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] };

export const PROCESSING_STATUS_LABELS: Record<string, string> = {
  pending: 'Queued',
  processing: 'Processing',
  chunks_ready: 'Indexing',
  completed: 'Ready',
  failed: 'Failed',
};
```

**Task 46.8 — Define formatting utilities**

In `utils/format.ts`:
```typescript
export function formatFileSize(mb: number): string {
  if (mb < 1) return `${Math.round(mb * 1024)} KB`;
  return `${mb.toFixed(1)} MB`;
}

export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const diffMs = Date.now() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function formatProcessingTime(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function formatNumber(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}
```

**Error Verification — Phase 46:**

Create a temporary test page `app/test/page.tsx` that calls `workspaceService.list()` and renders the count. Start the FastAPI backend. Load the test page. Verify the workspace list appears. Trigger an API error (call with a fake workspace ID) and verify `ApiError` is thrown with correct `statusCode` and `detail` fields. Delete the test page after verification. Ensure zero TypeScript errors: run `tsc --noEmit`.

**Phase 46 Checklist:**
- [x] All five model files have zero TypeScript errors
- [x] `apiFetch` correctly handles 204 No Content responses
- [x] `apiFetch` does not set `Content-Type` for `FormData` bodies
- [x] `ApiError` carries `statusCode`, `errorType`, and `detail`
- [x] `workspaceService.list()` successfully fetches from the live backend
- [x] `documentService.upload()` sends `multipart/form-data` correctly
- [x] All constants are importable with correct types
- [x] `tsc --noEmit` reports zero errors

---

## Phase 47 — Global Layout and Navigation Shell

**Objective:** A persistent application shell consisting of a collapsible left sidebar (workspace history), a top bar with the workspace name and global controls (theme toggle, system status indicator), and a tab navigation bar (Chat / Documents / Analytics) that appears only within workspace pages.

**Technical Context:**

The layout hierarchy in Next.js App Router is: `app/layout.tsx` (root, always rendered) → `app/workspaces/[workspaceId]/layout.tsx` (workspace shell, rendered for all workspace sub-pages). This nesting is important: the root layout handles theme and fonts; the workspace layout handles the sidebar and tab navigation. The workspaces list page (`/workspaces`) does not have a sidebar — it is a full-width grid page.

The sidebar stores its collapsed/expanded state in `ui.store.ts` (Zustand). Collapsed state is also persisted to `localStorage` so the user's preference survives refreshes. The sidebar width transitions smoothly between `240px` (expanded) and `60px` (collapsed) using a CSS transition on `width` with `var(--motion-duration-emphasized)` and `var(--motion-easing-emphasized)` from tokens.

**Visual Design of the Sidebar:**
The sidebar uses `background: var(--md-sys-color-surface-container-low)` and a right `border: 1px solid var(--color-border)`. It has three sections: (1) a logo/app name at the top, (2) the workspace list in the middle (scrollable), and (3) a bottom section with the system health indicator and theme toggle. Each workspace item in the sidebar shows a colored dot (green = active, grey = archived), the workspace name (truncated with ellipsis when collapsed), and the document count badge. The active workspace item is highlighted with `background: var(--color-bg-hover)` and a left border accent of `3px solid var(--md-sys-color-primary)`.

**Micro-Tasks:**

**Task 47.1 — Build the Zustand UI store**

In `store/ui.store.ts`, define a Zustand store using `create`:
```typescript
interface UIState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (value: boolean) => void;
}
```
Initialize `sidebarCollapsed` from `localStorage.getItem('sidebar_collapsed') === 'true'`. In `toggleSidebar`, flip the state and persist to `localStorage`. Because Zustand initializers run on both server and client in Next.js, wrap the `localStorage` access in `typeof window !== 'undefined'` guard.

**Task 47.2 — Build the Zustand workspace store**

In `store/workspace.store.ts`, define:
```typescript
interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  isLoading: boolean;
  error: string | null;
  setWorkspaces: (ws: Workspace[]) => void;
  setActiveWorkspace: (id: string) => void;
  addWorkspace: (ws: Workspace) => void;
  removeWorkspace: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (err: string | null) => void;
}
```
This store is the single source of truth for workspace data across the app. The workspace list page and the sidebar both read from this store, preventing duplicate fetches.

**Task 47.3 — Build the `Sidebar` component**

In `components/layout/Sidebar.tsx`, this is a Client Component. It reads `workspaces` from `workspace.store`, the current path from `usePathname()` to determine the active workspace, and `sidebarCollapsed` from `ui.store`.

The sidebar is a fixed-position `<aside>` element with `height: 100vh`, `width: var(--sidebar-width)`, where `--sidebar-width` is a CSS variable set inline as `240px` when expanded and `64px` when collapsed. Apply `transition: width var(--motion-duration-emphasized) var(--motion-easing-emphasized)` so the collapse animation is smooth. When collapsed, hide text with `overflow: hidden` and `opacity: 0` transition.

Each workspace item is a `<Link>` to `/workspaces/{workspace_id}/chat` with an `onClick` that calls `setActiveWorkspace(workspace_id)`. The active item is detected by checking if the current pathname includes the workspace ID.

The collapse toggle button is an icon button (`ChevronLeft` / `ChevronRight` from Lucide) positioned at the bottom of the top section. It calls `toggleSidebar()`.

**Task 47.4 — Build the `TopBar` component**

In `components/layout/TopBar.tsx`, this is a Client Component. It shows:
- The current workspace name (from `workspace.store.activeWorkspaceId` looked up in `workspaces` array), truncated to 30 characters.
- A `ThemeToggle` on the right.
- A small `SystemStatusDot` — a 8px circle, green when all systems healthy, orange when degraded, red when error. This dot pings `/api/v1/system/model-status` every 30 seconds using `useSystemHealth` hook (built in Phase 55). For now, initialize it as neutral grey.
- The app logo/name on the left when the sidebar is not visible.

Use `background: var(--md-sys-color-surface)`, `border-bottom: 1px solid var(--color-border)`, `height: 52px`. The top bar spans the full width of the content area (right of sidebar).

**Task 47.5 — Build the `TabNav` component**

In `components/layout/TabNav.tsx`, a Client Component. Renders three tab links for the workspace sub-pages: Chat, Documents, Analytics. Uses `usePathname()` to determine the active tab. Each tab uses a `<Link>` and is styled with:
- Inactive: `color: var(--color-text-secondary)`, no background.
- Active: `color: var(--color-text-primary)` with a `2px solid var(--md-sys-color-primary)` bottom border that slides in using a CSS `scaleX` transform animation.

Tab icons from Lucide: `MessageSquare` for Chat, `Files` for Documents, `BarChart3` for Analytics.

**Task 47.6 — Build the workspace-level layout**

In `app/workspaces/[workspaceId]/layout.tsx`, this is a Server Component that receives `{ children, params }`. Fetch the workspace data server-side using `workspaceService.get(params.workspaceId)`. If the workspace does not exist (ApiError with 404), use `notFound()` from `next/navigation`. Pass the workspace to a Client Component called `WorkspaceShell`.

In `components/layout/WorkspaceShell.tsx` (a Client Component), it initializes the `workspace.store` with the fetched workspace and renders the full layout: `Sidebar` on the left, a flex-column main area on the right containing `TopBar`, `TabNav`, and then `{children}` in a scrollable content region.

The layout uses CSS Grid: `grid-template-columns: var(--sidebar-width) 1fr` on the outer wrapper. The `--sidebar-width` CSS variable is updated in sync with the Zustand `sidebarCollapsed` state via an inline style on the grid container.

**Error Verification — Phase 47:**

Navigate to `/workspaces` — verify no sidebar appears (this page does not use the workspace layout). Navigate to `/workspaces/some-valid-id/chat` — verify the sidebar appears, the active workspace is highlighted, and the tab navigation shows the active Chat tab underlined. Click Documents and Analytics tabs — verify the URL changes and the active tab indicator moves. Collapse the sidebar — verify smooth animation and text disappears. Refresh the page — verify collapsed/expanded state is preserved. Navigate to a non-existent workspace ID — verify `notFound()` triggers a 404 page.

**Phase 47 Checklist:**
- [x] Sidebar is absent on the `/workspaces` root page
- [x] Sidebar appears on all workspace sub-pages
- [x] Active workspace is highlighted with left border accent
- [x] Sidebar collapse/expand animates smoothly
- [x] Collapsed state persists across page refreshes
- [x] `TabNav` active indicator moves when switching tabs
- [x] Top bar shows the correct workspace name
- [x] Invalid workspace ID triggers 404 page
- [x] Grid layout reflows correctly on sidebar toggle

---

## Phase 48 — Workspace Dashboard: Bento Grid of Workspace Cards

**Objective:** The `/workspaces` page renders all existing workspaces as an interactive bento-grid, supports creating new workspaces via a modal, and supports workspace deletion via a confirmation dialog. This is the application's entry point.

**Technical Context:**

The workspace dashboard is the first impression of the product. Its layout is a **responsive CSS Grid** (not Flexbox) with `grid-template-columns: repeat(auto-fill, minmax(320px, 1fr))` and `gap: var(--space-5)`. This creates the bento-grid feel: cards of equal height arranged in a flowing grid that adapts to screen width. When there are no workspaces, an `EmptyState` component with a call-to-action occupies the full grid area.

Each `WorkspaceCard` component shows the workspace name, description, document count, chunk count, storage used, and relative creation time. The card has `background: var(--color-bg-card)`, `border: 1px solid var(--color-border)`, `border-radius: var(--radius-large)`, and `box-shadow: var(--elevation-1)`. On hover, it transitions to `box-shadow: var(--elevation-2)` and `border-color: var(--color-accent)`. The hover transition uses `var(--motion-duration-standard)`.

The `CreateWorkspaceModal` is a centered modal overlay. The overlay uses `position: fixed`, `inset: 0`, `background: rgba(0,0,0,0.6)`, `backdrop-filter: blur(4px)`. The modal panel uses `background: var(--md-sys-color-surface-container)` with `border-radius: var(--radius-large)`. It contains a text input for workspace name and an optional textarea for description. Submit triggers `workspaceService.create()`.

**Micro-Tasks:**

**Task 48.1 — Build the `useWorkspaces` hook**

In `hooks/useWorkspaces.ts`, a Client Hook. Calls `workspaceService.list()` in a `useEffect` on mount. Manages `data`, `isLoading`, and `error` state locally. Also updates `workspace.store.setWorkspaces()` with the fetched data so the sidebar can read the same data without a second fetch. Returns `{ workspaces, isLoading, error, refetch }` where `refetch` re-calls the service function.

**Task 48.2 — Build the `WorkspaceCard` component**

In `components/workspace/WorkspaceCard.tsx`. Receives a `Workspace` object as prop. The entire card is wrapped in a Next.js `<Link href={/workspaces/${workspace.workspace_id}/chat}>` so clicking it navigates immediately. Inside the card:
- Top row: workspace name in `font-size: var(--font-size-lg)`, `font-weight: 600`, `color: var(--color-text-primary)`. Right-aligned: a delete button (trash icon, Lucide `Trash2`) that shows on hover (`opacity: 0` by default, `opacity: 1` on card hover via CSS group-hover pattern or a local `useState(isHovered)`). The delete button must `stopPropagation()` to prevent navigating to the workspace.
- Middle: description text in `color: var(--color-text-secondary)`, `font-size: var(--font-size-sm)`. Max 2 lines with `overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical`.
- Bottom row: three `Badge` components: document count (`Files` icon), chunk count (`Layers` icon), storage used (`HardDrive` icon). Plus the relative creation time aligned right.

The `Badge` component (built in Phase 49's shared components) is a small pill: `background: var(--md-sys-color-surface-container)`, `border-radius: var(--radius-pill)`, `padding: 2px 8px`, `font-size: var(--font-size-xs)`.

**Task 48.3 — Build the `CreateWorkspaceModal` component**

In `components/workspace/CreateWorkspaceModal.tsx`, a Client Component controlled via `isOpen: boolean` and `onClose: () => void` props. Inside, a controlled form: workspace name input (required, max 255 chars) and description textarea (optional). Form state uses `useState`. Submit handler calls `workspaceService.create()`, on success calls `refetch()` (passed as prop) and `onClose()`. On error, shows an inline error message below the input using the `ApiError.detail` string.

The modal uses Framer Motion for entrance/exit: `<AnimatePresence>` wrapping the overlay `<motion.div>` with `initial={{ opacity: 0 }}`, `animate={{ opacity: 1 }}`, `exit={{ opacity: 0 }}`. The modal panel uses `initial={{ scale: 0.95, opacity: 0 }}`, `animate={{ scale: 1, opacity: 1 }}` with `transition={{ duration: 0.15, ease: [0.2, 0, 0, 1] }}` (matching `var(--motion-easing-standard)`).

Close on backdrop click and on `Escape` key (add a `useEffect` that adds/removes a `keydown` listener when `isOpen` changes).

**Task 48.4 — Build the `WorkspaceDeleteDialog` component**

In `components/workspace/WorkspaceDeleteDialog.tsx`. A smaller modal (max-width 400px) with a warning icon (`AlertTriangle` from Lucide, color `var(--md-sys-color-error)`), the workspace name in bold, and a warning that this deletes all documents, chunks, and conversation history permanently. Two buttons: "Cancel" (secondary style) and "Delete Workspace" (destructive style: `background: var(--md-sys-color-error-container)`, `color: var(--md-sys-color-on-error-container)`). On confirm, calls `workspaceService.delete(workspaceId)`, then updates the store with `removeWorkspace(workspaceId)` and calls `refetch()`.

**Task 48.5 — Build the `WorkspaceGrid` component and the page**

In `components/workspace/WorkspaceGrid.tsx`, receives `workspaces: Workspace[]`, `onDelete: (id: string) => void`, `refetch: () => void`. Renders the CSS Grid container with the cards. Manages local state for which workspace's delete dialog is open.

In `app/workspaces/page.tsx`, a Client Component that uses `useWorkspaces()`. Shows a full-page centered `Spinner` during loading. Shows an `EmptyState` with a "Create your first workspace" message and a large Create button when the list is empty. Shows the `WorkspaceGrid` when data exists. A "New Workspace" button in the top-right opens the `CreateWorkspaceModal`. The page header shows "Workspaces" as an `h1` and the total count.

**Task 48.6 — Build shared primitive components**

Build these in `components/shared/` as they are needed by Phase 48 and all subsequent phases.

`Button.tsx`: supports `variant` prop (`'primary' | 'secondary' | 'ghost' | 'destructive'`), `size` prop (`'sm' | 'md' | 'lg'`), `isLoading` prop that replaces children with a `Spinner` and disables the button, and `leftIcon` / `rightIcon` slots. Style using CSS variables. Primary: `background: var(--md-sys-color-primary)`, `color: var(--md-sys-color-on-primary)`. Secondary: `background: var(--color-bg-input)`, `border: 1px solid var(--color-border)`. Ghost: transparent background with hover. Destructive: error colors.

`Badge.tsx`: pill-shaped label with optional icon. Props: `label: string`, `icon?: ReactNode`, `variant?: 'default' | 'success' | 'warning' | 'error'`. Each variant maps to a token color pair.

`Spinner.tsx`: a CSS animation using `@keyframes spin` on a circular border element. The spinning border uses `border: 2px solid var(--color-border)` with `border-top-color: var(--md-sys-color-primary)`. Size props: `'sm' | 'md' | 'lg'`.

`Modal.tsx`: a generic modal wrapper that handles the overlay, backdrop blur, Framer Motion entrance/exit, and `Escape` key close. Receives `isOpen`, `onClose`, `title`, `children`. All modals in the app use this wrapper.

`EmptyState.tsx`: centered illustration area with a title, description, and optional action button. Use a simple SVG or a Lucide icon in large size as the illustration.

**Error Verification — Phase 48:**

With the backend running and having at least two workspaces, load `/workspaces`. Verify the bento grid renders both cards. Click "New Workspace", fill the form, submit — verify the new card appears without a full page reload (refetch updates the store). Click the delete icon on a card — verify the confirmation dialog opens. Cancel — verify no deletion. Confirm — verify the card disappears and the workspace is gone from the backend. Test creating a workspace with an empty name — verify the form does not submit and shows a validation error.

**Phase 48 Checklist:**
- [x] Workspace cards render with all metadata (docs, chunks, storage)
- [x] CSS Grid layout adapts to different screen widths
- [x] Create modal opens, submits, and adds the card without full page reload
- [x] Delete dialog shows workspace name and warns about data loss
- [x] Delete confirmation removes the card and deletes from backend
- [x] Empty name validation prevents submission and shows inline error
- [x] `EmptyState` shows when no workspaces exist
- [x] Modal close on `Escape` key and backdrop click works
- [x] Framer Motion entrance animation plays on modal open

---

## Phase 49 — Workspace Detail Layout and Document Explorer

**Objective:** The Documents tab (`/workspaces/[workspaceId]/documents`) provides a full document management interface: drag-and-drop upload area, a sortable table of uploaded documents with processing status, and delete confirmation. The `ProcessingStatus` component polls the backend until `completed` or `failed`.

**Technical Context:**

Document management is the second most critical workflow after chat. Users upload PDFs and DOCXs here, watch them process, and then switch to the chat tab. The UX must minimize perceived waiting time by showing granular status transitions: Queued → Processing → Indexing → Ready.

The `DropZone` uses `react-dropzone`. It validates file types against `ACCEPTED_FILE_TYPES` and file size against `MAX_FILE_SIZE_MB` *on the client side* before sending to the backend. This prevents a round trip for obviously invalid files. The drop zone has a dashed border (`border: 2px dashed var(--md-sys-color-outline)`) that changes to `var(--md-sys-color-primary)` when a file is dragged over it. The transition uses `var(--motion-duration-fast)`.

The document table is not a `<table>` element — it is a CSS Grid layout with header row and data rows. This gives full control over column widths and hover states. Use `grid-template-columns: 2fr 80px 100px 120px 60px` for: Name, Size, Chunks, Status, Actions.

**Micro-Tasks:**

**Task 49.1 — Build the `useDocuments` hook**

In `hooks/useDocuments.ts`. Fetches `documentService.listByWorkspace(workspaceId)` on mount and when `workspaceId` changes. Exposes `documents`, `isLoading`, `error`, and `refetch`. Also manages an `uploadingDocuments: Set<string>` set of document IDs currently being polled.

**Task 49.2 — Build the `usePolling` hook**

In `hooks/usePolling.ts`. A generic hook that takes a callback function and interval. Calls the callback on mount and then every `interval` milliseconds. Clears the interval on unmount. Returns `{ stop, start }` controls. Used by document status polling and system health polling.

```typescript
export function usePolling(callback: () => void, intervalMs: number, active: boolean = true) {
  useEffect(() => {
    if (!active) return;
    callback(); // Call immediately
    const id = setInterval(callback, intervalMs);
    return () => clearInterval(id);
  }, [callback, intervalMs, active]);
}
```

The `active` parameter allows pausing polling when the document is complete or the tab is not visible.

**Task 49.3 — Build the `DropZone` component**

In `components/documents/DropZone.tsx`. Uses `useDropzone` from `react-dropzone` with `accept: ACCEPTED_FILE_TYPES`, `maxSize: MAX_FILE_SIZE_MB * 1024 * 1024`, `multiple: true`. The `onDrop` callback receives `acceptedFiles` and `rejectedFiles`. For each accepted file, call `documentService.upload(workspaceId, file)` and trigger a refetch when done. For rejected files, show a toast-like inline error.

Visual states: idle (dashed border, `CloudUpload` icon, "Drop PDF or DOCX files here" text), active drag over (solid border, primary color, scale slightly), uploading (show progress indicator). Use Framer Motion's `whileHover={{ scale: 1.01 }}` on the drop zone container.

**Task 49.4 — Build the `DocumentRow` and `ProcessingStatus` components**

`ProcessingStatus.tsx` is a small indicator component that receives a `ProcessingStatus` value and renders: a colored `Badge` (green for completed, yellow for processing/chunks_ready, red for failed, grey for pending) with the label from `PROCESSING_STATUS_LABELS`. For non-terminal statuses (pending, processing, chunks_ready), it also shows a small pulsing animation: a CSS `@keyframes pulse` on the badge background opacity.

`DocumentRow.tsx` receives a `Document` object. Renders the document file name (with a `FileText` or `File` icon based on type), file size (formatted with `formatFileSize`), chunk count, processing status, and a delete button. The delete button opens a `DocumentDeleteDialog`. If `processing_status` is `'processing'` or `'chunks_ready'`, the delete button is disabled.

When `processing_status` is not `'completed'` and not `'failed'`, the row triggers polling. Use `usePolling` inside `DocumentRow` to call `documentService.getStatus(document_id)` every `POLLING_INTERVAL_MS` milliseconds and update the document in the store/parent state when status changes. Stop polling when the terminal status is reached.

**Task 49.5 — Build the `DocumentTable` component**

In `components/documents/DocumentTable.tsx`. Receives `documents: Document[]`. Renders a header row with column labels and then a list of `DocumentRow` components. Apply a hover background of `var(--color-bg-hover)` to each row using CSS. Show an `EmptyState` ("No documents yet — upload some above") when the array is empty. Sort documents by `upload_time` descending (newest first).

**Task 49.6 — Build the Documents page**

In `app/workspaces/[workspaceId]/documents/page.tsx`, a Client Component. Composes `DropZone` at the top (with a brief title "Upload Documents"), followed by a divider, then `DocumentTable`. Uses `useDocuments(workspaceId)` for data. The `workspaceId` is obtained from `useParams()`.

**Error Verification — Phase 49:**

Upload a PDF smaller than 50MB. Verify the status transitions from Queued → Processing → Indexing → Ready without any manual refresh (polling works). Try uploading a `.txt` file — verify client-side rejection with an inline error before any network request. Try uploading a file over 50MB — verify client-side rejection. Delete a completed document — verify it disappears from the table. Verify that a document in "Processing" state has a disabled delete button.

**Phase 49 Checklist:**
- [x] Drag-and-drop area accepts PDF and DOCX only
- [x] Client-side file type and size validation prevents invalid uploads
- [x] Status transitions animate through all stages without manual refresh
- [x] Polling stops when status reaches `completed` or `failed`
- [x] `ProcessingStatus` shows correct color for each status
- [x] Delete dialog shows for completed documents; button is disabled for processing ones
- [x] Document table renders correctly with all column data
- [x] Empty state shows when no documents exist

---

## Phase 50 — Chat Interface: Core Visual Layout

**Objective:** Build the complete visual structure of the chat interface — message list, message bubbles, the input area, and the mode selector — without yet connecting any backend API calls. This phase focuses on the visual and interaction patterns.

**Technical Context:**

The chat interface is the most complex and most-used part of the application. It has three visual regions arranged vertically: (1) a scrollable message history area that grows from the top, (2) an optional source citation panel that appears when an assistant message has retrieval data, and (3) a sticky bottom input area.

The message list uses CSS `flex-direction: column` with `justify-content: flex-start`. New messages are appended at the bottom. Auto-scroll to the bottom on new messages using a `scrollIntoView` call on a `useRef` attached to a sentinel `<div>` at the very end of the list. Importantly, do **not** auto-scroll if the user has manually scrolled up — detect this by checking `scrollTop + clientHeight < scrollHeight - threshold` before auto-scrolling.

**Message bubble design:** User messages align right with `background: var(--md-sys-color-surface-container)`. Assistant messages align left with `background: var(--color-bg-card)` and `box-shadow: var(--glow-ai-subtle)` (the AI content glow token from `tokens.css`). This subtle glow differentiates AI content visually. Both use `border-radius: var(--radius-large)` but with one corner made sharp to indicate the speaker side (user = top-right sharp, assistant = top-left sharp).

**Micro-Tasks:**

**Task 50.1 — Build the Zustand chat store**

In `store/chat.store.ts`:
```typescript
interface ChatState {
  // Keyed by workspaceId to support multiple workspaces
  messages: Record<string, Message[]>;
  isLoading: Record<string, boolean>;      // workspace is awaiting response
  pendingQuery: Record<string, string>;   // the query currently being processed
  mode: ChatMode;
  setMessages: (workspaceId: string, messages: Message[]) => void;
  appendMessage: (workspaceId: string, message: Message) => void;
  setLoading: (workspaceId: string, loading: boolean) => void;
  setMode: (mode: ChatMode) => void;
}
```

The `Record<string, ...>` keying by `workspaceId` is critical for workspace isolation. Switching workspaces should show that workspace's chat history, not bleed data between workspaces.

**Task 50.2 — Build the `MessageBubble` component**

In `components/chat/MessageBubble.tsx`. Receives a `Message` object. For user messages: right-aligned `<div>` with `align-self: flex-end`, the message text in a bubble. For assistant messages: left-aligned with `align-self: flex-start`. The assistant bubble contains:
- The Markdown-rendered response (using `MarkdownRenderer` from shared components, built in Phase 51).
- A footer row showing: model used (small badge: `var(--font-size-xs)`, `color: var(--color-text-tertiary)`), retrieval chunks count (`Layers` icon + count), and the relative timestamp.
- The AI glow: `box-shadow: var(--glow-ai-subtle)` that transitions to `var(--glow-ai-medium)` on hover.

Use Framer Motion for message entrance: `initial={{ opacity: 0, y: 8 }}`, `animate={{ opacity: 1, y: 0 }}`, `transition={{ duration: 0.2 }}`. Stagger is not needed since messages appear one at a time.

**Task 50.3 — Build the `MessageList` component**

In `components/chat/MessageList.tsx`. Receives `messages: Message[]` and `isLoading: boolean`. Renders a scrollable container with `overflow-y: auto`, `flex: 1`. Maps messages to `MessageBubble` components. At the end, when `isLoading` is true, shows a "thinking" indicator: three pulsing dots using a CSS animation. The dots use `background: var(--color-text-tertiary)`. The sentinel `<div ref={bottomRef} />` is placed after the thinking indicator.

Auto-scroll logic: in a `useEffect` that runs when `messages` or `isLoading` changes, check the scroll position before scrolling. Only call `bottomRef.current.scrollIntoView({ behavior: 'smooth' })` if the container is within 100px of the bottom.

**Task 50.4 — Build the `ModeSelector` component**

In `components/chat/ModeSelector.tsx`. A row of three segmented buttons using `CHAT_MODES`. The active mode is highlighted with `background: var(--md-sys-color-primary)`, `color: var(--md-sys-color-on-primary)`. Inactive modes use `background: transparent` with hover state. Reads and writes to `chat.store.mode`. Include a `Tooltip` component (built below) that shows the `description` from `CHAT_MODES` on hover over each segment.

**Task 50.5 — Build the `ChatInput` component**

In `components/chat/ChatInput.tsx`. A `<textarea>` that auto-resizes vertically as the user types (up to a max of 6 rows). Use a `useEffect` that sets the textarea's `height: auto` then `height: scrollHeight + 'px'` every time the value changes. This creates the "growing textarea" pattern.

The input area: `background: var(--color-bg-input)`, `border: 1px solid var(--color-border)`, `border-radius: var(--radius-large)`. On focus, `border-color: var(--md-sys-color-primary)`. Press `Enter` (without Shift) submits; `Shift+Enter` adds a newline. Disabled when `isLoading` is true. A `Send` button (Lucide `ArrowUp` icon in a circle) is positioned inside the textarea's bottom-right corner. The button pulses with a subtle animation when `isLoading`.

**Task 50.6 — Build the `EmptyConversation` component**

In `components/chat/EmptyConversation.tsx`. Shown when there are no messages yet. Centered content: a large icon, workspace name, "Ask anything about your documents" subtitle. Three example query cards below (for research/academic context): "Summarize the key findings", "Compare the methodologies used", "What are the limitations discussed". Clicking an example query pre-fills the `ChatInput`. These are static suggestions — do not call the backend.

**Task 50.7 — Build the `ChatContainer` and the chat page**

In `components/chat/ChatContainer.tsx`, the orchestrator that composes `MessageList` + `ChatInput` + `ModeSelector`. Uses flexbox column layout: `ModeSelector` at top (compact, right-aligned), `MessageList` in the middle (flex: 1, scrollable), `ChatInput` at the bottom (sticky).

In `app/workspaces/[workspaceId]/chat/page.tsx`: a Client Component that uses `useChat(workspaceId)` hook (built in Phase 52) and renders `ChatContainer`. If the workspace has no documents, show a `Banner` warning: "Upload documents first to enable AI-powered answers" with a link to the Documents tab.

**Task 50.8 — Build the `Tooltip` component**

In `components/shared/Tooltip.tsx`. A simple wrapper that uses CSS `position: relative`. The tooltip text appears in a `::after`-style `<span>` that is `position: absolute`, `background: var(--md-sys-color-surface-container-highest)`, `border-radius: var(--radius-standard)`, `padding: var(--space-2) var(--space-3)`, `white-space: nowrap`. Toggled via CSS `opacity` on parent `hover`. No JavaScript needed.

**Error Verification — Phase 50:**

The chat interface should render visually at this point. Add some mock messages directly to the chat store to test rendering. Verify user and assistant bubbles align correctly. Verify the AI glow is visible on assistant bubbles. Verify the textarea grows and resets on submit. Verify `Enter` submits (handled in Phase 52) and `Shift+Enter` adds a newline. Verify the mode selector updates the store correctly.

**Phase 50 Checklist:**
- [x] User bubbles align right, assistant bubbles align left
- [x] Assistant bubbles show AI glow tokens from `tokens.css`
- [x] Textarea auto-resizes up to 6 rows
- [x] `Enter` submits; `Shift+Enter` adds newline
- [x] Mode selector updates `chat.store.mode` and highlights correctly
- [x] Auto-scroll only triggers when near the bottom of the message list
- [x] Thinking indicator shows when `isLoading` is true
- [x] `EmptyConversation` shows when no messages exist
- [x] Framer Motion entrance animation plays on new messages

---

## Phase 51 — Markdown Renderer and Source Citation Panel

**Objective:** Build the `MarkdownRenderer` that transforms raw LLM Markdown output into rich, styled HTML with syntax-highlighted code blocks, proper table styling, and citation link rendering. Build the `SourceCitationPanel` that displays the retrieved source documents for each assistant response.

**Technical Context:**

The LLM returns Markdown with headings, bullet lists, numbered lists, code blocks, tables, and citation references like `[1]`, `[2]`. The `MarkdownRenderer` uses `react-markdown` with the `remark-gfm` plugin (for tables, task lists, strikethrough) and `rehype-highlight` (for code syntax highlighting). All elements rendered by `react-markdown` are customized via its `components` prop to use CSS variables instead of default browser styles.

The key challenge: `react-markdown` renders raw HTML elements (`h1`, `p`, `ul`, `code`, `table`). These need to be styled using the design token system. Define all Markdown styles in a scoped CSS class `.md-content` in `styles/globals.css`. Every element inside `.md-content` uses tokens: headings use `var(--font-size-xl)` and `var(--color-text-primary)`, code blocks use `var(--md-sys-color-surface-container-lowest)` background and `font-family: var(--font-mono)`.

The source citation panel is a collapsible panel below each assistant message, toggled by a "Sources" button. It shows each source document as a card with the filename and how many chunks were retrieved from it. This is parsed from the source attribution text appended to the response by the backend.

**Micro-Tasks:**

**Task 51.1 — Add Markdown styles to globals.css**

After the token imports in `globals.css`, add a `.md-content` block. Style every Markdown element using tokens:
- `h1, h2, h3`: `font-size` from the scale, `color: var(--color-text-primary)`, `margin-top: var(--space-5)`, `font-weight: 600`.
- `p`: `color: var(--color-text-secondary)`, `line-height: var(--line-height-relaxed)`, `margin-bottom: var(--space-3)`.
- `ul, ol`: `padding-left: var(--space-5)`, `color: var(--color-text-secondary)`.
- `li`: `margin-bottom: var(--space-1)`.
- `code` (inline): `background: var(--md-sys-color-surface-container)`, `border-radius: var(--radius-sharp)`, `padding: 2px 6px`, `font-family: var(--font-mono)`, `font-size: 0.9em`.
- `pre`: `background: var(--md-sys-color-surface-container-lowest)`, `border-radius: var(--radius-standard)`, `padding: var(--space-4)`, `overflow-x: auto`, `border: 1px solid var(--color-border)`.
- `pre code`: `background: none`, `padding: 0`, `font-size: var(--font-size-sm)`, `line-height: var(--line-height-relaxed)`.
- `table`: `width: 100%`, `border-collapse: collapse`.
- `th`: `background: var(--md-sys-color-surface-container)`, `padding: var(--space-2) var(--space-3)`, `text-align: left`, `font-weight: 600`, `border-bottom: 1px solid var(--color-border)`.
- `td`: `padding: var(--space-2) var(--space-3)`, `border-bottom: 1px solid var(--color-border-subtle)`.
- `tr:hover`: `background: var(--color-bg-hover)`.
- `blockquote`: `border-left: 3px solid var(--md-sys-color-primary)`, `padding-left: var(--space-3)`, `color: var(--color-text-tertiary)`.
- `strong`: `color: var(--color-text-primary)`, `font-weight: 600`.
- `a`: `color: var(--md-sys-color-tertiary)`, `text-decoration: underline`.
- `hr`: `border: none`, `border-top: 1px solid var(--color-border)`.

**Task 51.2 — Build the `MarkdownRenderer` component**

In `components/shared/MarkdownRenderer.tsx`. Imports `ReactMarkdown`, `remarkGfm`, `rehypeHighlight`. Wraps output in a `<div className="md-content">`. Passes `remark-gfm` to the `remarkPlugins` array and `rehype-highlight` to `rehypePlugins`. The `components` prop customizes how links are rendered: open in a new tab with `target="_blank" rel="noopener noreferrer"`.

Also detect citation references `[1]`, `[2]` in the text and render them as `<sup>` elements with a `var(--md-sys-color-tertiary)` color. This is a preprocessing step: before passing the content string to `ReactMarkdown`, run a regex replace: `/\[(\d+)\]/g` → `<sup>[{n}]</sup>`. However, be careful not to replace Markdown link syntax `[text](url)`. The safe regex is `/\[(\d+)\](?!\()/g`.

**Task 51.3 — Build the `SourceCitationPanel` component**

In `components/chat/SourceCitationPanel.tsx`. Parses the sources text appended to the response by the backend (format: `"Sources: [1] filename.pdf (3 chunks), [2] doc.docx (1 chunk)"`). Use a regex to extract filename and chunk count pairs. Renders a collapsible panel using a `<details>/<summary>` HTML element (or Framer Motion `AnimatePresence` with a height animation). Inside, shows each source as a row: a `FileText` icon, the filename, and a small `(n chunks)` badge. Defaults to closed.

The panel's trigger is a small button inside the assistant message footer: "Sources (n)" where n is the number of sources. Clicking it toggles the panel open/closed using `useState`.

**Error Verification — Phase 51:**

Create a test message in the chat store with a long Markdown response including headings, code blocks, a table, and bold/italic text. Verify all elements render with the correct CSS variable styles in both dark and light themes. Verify code blocks have syntax highlighting. Verify the source citation panel parses and displays sources correctly. Test in both themes to confirm tokens apply correctly.

**Phase 51 Checklist:**
- [x] All Markdown elements render using CSS variable tokens
- [x] Code blocks use monospace font and dark background
- [x] Tables render with hover states on rows
- [x] Citation references `[1]` render as superscripts
- [x] Source citation panel parses "Sources:" footer text correctly
- [x] Panel collapses and expands with animation
- [x] Styles are correct in both dark and light themes

---

## Phase 52 — Chat Integration: Backend Connection and State Management

**Objective:** Wire the chat interface to the backend. Load conversation history on mount, handle query submission with optimistic UI updates, show the loading/thinking state, and handle all error cases gracefully.

**Technical Context:**

The query submission flow is a critical UX pattern. Do **not** wait for the backend response before showing the user's message. Instead, use optimistic UI: the moment the user submits, immediately append the user's message to the message list with a temporary client-generated ID (`crypto.randomUUID()`). Then show the thinking indicator. When the backend responds, append the assistant message. If the backend fails, remove the optimistic user message and show an error notification in-line.

This approach makes the UI feel instant and responsive even when the backend takes 3-10 seconds for a full RAG pipeline run.

History loading: on mount, call `chatService.getHistory(workspaceId)`. If the history is empty, show `EmptyConversation`. Store messages in `chat.store` keyed by `workspaceId`. Do not re-fetch history on every render — fetch once on mount and append from there.

**Micro-Tasks:**

**Task 52.1 — Build the `useChat` hook**

In `hooks/useChat.ts`, the central hook for chat functionality:

```typescript
export function useChat(workspaceId: string) {
  const { messages, setMessages, appendMessage, isLoading, setLoading, mode } = useChatStore();
  const [error, setError] = useState<string | null>(null);
  
  // Workspace-scoped messages
  const workspaceMessages = messages[workspaceId] ?? [];
  const workspaceLoading = isLoading[workspaceId] ?? false;

  // Load history on mount
  useEffect(() => {
    chatService.getHistory(workspaceId)
      .then(data => setMessages(workspaceId, data.messages))
      .catch(err => setError(err.detail));
  }, [workspaceId]);

  const sendQuery = useCallback(async (query: string) => {
    if (!query.trim() || workspaceLoading) return;

    // Optimistic user message
    const tempUserMessage: Message = {
      message_id: crypto.randomUUID(),
      workspace_id: workspaceId,
      role: 'user',
      message: query,
      created_at: new Date().toISOString(),
      retrieval_chunks: 0,
    };
    appendMessage(workspaceId, tempUserMessage);
    setLoading(workspaceId, true);
    setError(null);

    try {
      const response = await chatService.query({ workspace_id: workspaceId, query, mode });
      
      const assistantMessage: Message = {
        message_id: crypto.randomUUID(),
        workspace_id: workspaceId,
        role: 'assistant',
        message: response.response,
        model_used: response.model_used,
        created_at: new Date().toISOString(),
        retrieval_chunks: response.retrieval_chunks,
      };
      appendMessage(workspaceId, assistantMessage);
    } catch (err) {
      // Remove optimistic message on failure
      setMessages(workspaceId, workspaceMessages);
      const apiErr = err as ApiError;
      setError(apiErr.detail ?? 'Query failed. Please try again.');
    } finally {
      setLoading(workspaceId, false);
    }
  }, [workspaceId, workspaceLoading, mode]);

  return { messages: workspaceMessages, isLoading: workspaceLoading, error, sendQuery };
}
```

**Task 52.2 — Connect `ChatContainer` and `ChatInput` to `useChat`**

Update `ChatContainer` to accept the `useChat` return value. Pass `sendQuery` to `ChatInput`'s `onSubmit`. Pass `messages` and `isLoading` to `MessageList`. Pass `error` to a small inline error banner shown above the input area when non-null. The error banner uses `color: var(--md-sys-color-error)` and a `X` dismiss button.

**Task 52.3 — Build the `ChatInput` submit handler in context**

In `ChatInput`, call `onSubmit(inputValue)` and immediately clear `inputValue` state (reset textarea to empty). The textarea is disabled when `isLoading` is true. The submit button shows a `Spinner` when `isLoading` instead of the arrow icon.

**Task 52.4 — Handle the "no documents" warning**

In the chat page, before rendering `ChatContainer`, check if the workspace has `total_documents === 0`. Read this from `workspace.store`. If zero, render a non-dismissable banner above the chat interface: `background: var(--md-sys-color-tertiary-container)`, `color: var(--md-sys-color-on-tertiary-container)`, with a `BookOpen` icon and text "No documents uploaded yet. Go to Documents to upload files." with a `<Link>` to the documents tab. Still allow the chat interface to render below — the user can still query (the backend handles empty workspaces gracefully).

**Error Verification — Phase 52:**

With the backend running and a workspace with at least one completed document, submit a query. Verify: (1) user message appears instantly, (2) thinking indicator shows, (3) assistant response appears with Markdown rendered, (4) retrieval chunks count in the footer matches the backend response. Test with Groq API key invalid — verify the error banner appears with a readable message rather than a crash. Test submitting when `isLoading` — the input must be disabled and the button must not fire the query again.

**Phase 52 Checklist:**
- [x] Conversation history loads on mount from the backend
- [x] User message appears optimistically before backend responds
- [x] Thinking indicator shows during backend processing
- [x] Assistant response renders as Markdown with source citations
- [x] Error banner shows on backend failure with readable message
- [x] Double-submit is prevented when `isLoading` is true
- [x] Workspace isolation: switching workspaces shows correct history
- [x] Processing time and model used appear in assistant message footer

---

## Phase 53 — Mode Selector Integration and Prompt Mode Persistence

**Objective:** Ensure the mode selector (Simple / Medium / Expert) correctly persists the user's preference, passes it to the query API, and visually communicates the capability level of each mode.

**Technical Context:**

The mode selection is already built visually in Phase 50 and wired to the store in Phase 52. This phase focuses on persistence and the informational UX around modes. The user's last-used mode should persist in `localStorage` so it survives refreshes. The mode selector should also clearly communicate what each mode does — Simple uses the local Qwen model (fast, offline), Expert uses Groq with a large model (best quality but uses API credits).

The model used in the last response is shown in the assistant message footer. When the system falls back from Groq to Qwen (failover), the message footer will show `"qwen"` instead of the expected `"groq"`. The UI should display this naturally without alarming the user.

**Micro-Tasks:**

**Task 53.1 — Persist mode selection in `chat.store`**

Update `chat.store.ts` to initialize `mode` from `localStorage.getItem('chat_mode') as ChatMode ?? 'medium'`. In the `setMode` action, also call `localStorage.setItem('chat_mode', mode)`. Wrap the `localStorage` access in a `typeof window !== 'undefined'` guard for SSR safety.

**Task 53.2 — Enhance `ModeSelector` with tooltips and model indicators**

Update `ModeSelector.tsx` to wrap each mode button in the `Tooltip` component. The tooltip content shows: for Simple — "Uses local Qwen model. Fast and offline."; for Medium — "Uses Groq API. Balanced speed and quality."; for Expert — "Uses Groq large model. Best for complex analysis." Additionally, show a small colored dot next to each label when selected: green for Simple (local), blue for Medium (cloud), purple for Expert (cloud).

**Task 53.3 — Display model name in message footer**

Update `MessageBubble.tsx` to show the model name with a visual treatment. Map model names to display strings: if `model_used` contains "groq" → "Groq", if it contains "qwen" → "Local (Qwen)", if it is "none" → "Unavailable". Apply appropriate color: Groq = `var(--md-sys-color-tertiary)`, Local = `var(--md-sys-color-secondary)`.

**Error Verification — Phase 53:**

Submit queries in all three modes. Verify the correct model name appears in the footer. Change mode between queries and verify mode persists on page refresh. Hover over each mode button and verify tooltip appears. If Qwen is not running (Ollama not active), submit in Simple mode and verify the fallback to Groq message appears in the response footer.

**Phase 53 Checklist:**
- [x] Mode persists in `localStorage` and survives page refresh
- [x] Each mode button shows a tooltip with model information
- [x] Model name in the message footer maps to a human-readable label
- [x] Mode is correctly passed to `chatService.query()`
- [x] Switching modes mid-conversation works (next query uses the new mode)

---

## Phase 54 — Analytics Dashboard: Bento Visualization Grid

**Objective:** Build the Analytics tab as a bento-grid of metric cards and charts that visualize workspace usage: total queries, model usage breakdown, document stats, storage usage, and chunk count.

**Technical Context:**

The analytics dashboard is a read-only visualization page. It calls `analyticsService.get(workspaceId)` once on mount and on a 30-second refresh interval. It does not need real-time polling at high frequency — analytics are not time-critical. Use `usePolling` with a 30-second interval.

The bento layout uses CSS Grid with `grid-template-areas` for precise placement of differently-sized cards. The grid has two sizes of cards: standard cards (1×1) for scalar metrics, and wider cards (2×1 or spanning) for charts. This creates the bento asymmetry that makes dashboards visually interesting.

**Grid layout:**
```
"queries  documents chunks    storage"
"model    model     model-chart model-chart"
```

Recharts is used for the model usage bar chart. The chart uses the token colors for bars: Groq bars use `var(--md-sys-color-primary)`, local model bars use `var(--md-sys-color-secondary)`. Pass `style={{ color: 'var(--color-text-primary)' }}` to chart components so text respects the theme.

**Micro-Tasks:**

**Task 54.1 — Build the `useAnalytics` hook**

In `hooks/useAnalytics.ts`. Calls `analyticsService.get(workspaceId)` on mount. Uses `usePolling` with 30-second interval. Returns `{ analytics, isLoading, error, lastUpdated }`. Formats `last_updated` using `formatRelativeTime`.

**Task 54.2 — Build the `StatCard` component**

In `components/analytics/StatCard.tsx`. Receives `title: string`, `value: number | string`, `icon: ReactNode`, `subtitle?: string`, `trend?: 'up' | 'down' | 'neutral'`. Renders a card with `background: var(--color-bg-card)`, `border-radius: var(--radius-large)`, `padding: var(--space-5)`. The value is large (`font-size: var(--font-size-2xl)`, `font-weight: 700`). The icon is shown in a small circle with `background: var(--md-sys-color-surface-container)`. Uses Framer Motion `initial={{ opacity: 0, scale: 0.95 }}` entrance animation with a staggered delay based on card index.

**Task 54.3 — Build the `ModelUsageChart` component**

In `components/analytics/ModelUsageChart.tsx`. Uses Recharts `BarChart` with two bars: Groq requests and local model requests. Chart container uses `ResponsiveContainer width="100%" height={160}`. Axis labels use `fill: var(--color-text-tertiary)`. Bar fill colors read from `getComputedStyle(document.documentElement).getPropertyValue('--md-sys-color-primary')` to respect the current theme — this must be done inside a `useEffect` or a computed style read, not hardcoded.

**Task 54.4 — Build the `StorageBar` component**

In `components/analytics/StorageBar.tsx`. A horizontal progress-bar style component showing `total_storage_mb` against a nominal max of 500MB (or the actual max for the deployment). The bar fills from left to right. Color transitions from `var(--md-sys-color-secondary)` at 0% to `var(--md-sys-color-error)` at >80% using a CSS `linear-gradient`. Shows the formatted storage value (`formatFileSize(total_storage_mb)`) below.

**Task 54.5 — Build the `AnalyticsBento` component and page**

In `components/analytics/AnalyticsBento.tsx`. Composes the CSS Grid with all stat cards and charts in the defined layout. During loading, show skeleton placeholders: `<div>` elements with `background: var(--color-bg-hover)`, `border-radius: var(--radius-standard)`, and a CSS shimmer animation (`@keyframes shimmer` that animates a `linear-gradient` across the element).

In `app/workspaces/[workspaceId]/analytics/page.tsx`, a Client Component using `useAnalytics(workspaceId)`. Renders the `AnalyticsBento` component plus a `last updated` timestamp in the top-right corner.

**Error Verification — Phase 54:**

Navigate to the Analytics tab of a workspace that has been used (queries submitted). Verify all four stat cards render with correct values. Submit three more queries and refresh analytics (or wait 30 seconds for the auto-refresh) — verify `total_queries` increases. Verify the chart renders correctly. Toggle the theme and verify chart colors adapt. Test the loading skeleton by adding an artificial delay.

**Phase 54 Checklist:**
- [x] All four `StatCard` components render with correct values from the backend
- [x] `ModelUsageChart` renders bars for both Groq and local model
- [x] Chart colors adapt to dark/light theme
- [x] `StorageBar` shows correct percentage and turns red above 80%
- [x] Loading skeleton shows during data fetch
- [x] Auto-refresh updates analytics every 30 seconds
- [x] `last_updated` timestamp shows in relative format

---

## Phase 55 — System Health Monitor and Status Indicators

**Objective:** Build the `/system` page as a full health dashboard and wire the `SystemStatusDot` in the top bar to reflect real subsystem health in real time.

**Technical Context:**

The system health page is used by technical users (the researcher/student who deployed the system) to understand whether all components are operational. It shows four subsystems: database, embedding model, Groq API, and local Qwen model. Each subsystem shows its status as a colored indicator and optionally a detail message.

The `SystemStatusDot` in the `TopBar` (built as a placeholder in Phase 47) now polls `/api/v1/system/model-status` every 30 seconds via `useSystemHealth`. If any subsystem has `status: 'error'`, the dot turns red. If `status: 'degraded'`, orange. All `'ok'` → green.

**Micro-Tasks:**

**Task 55.1 — Build the `useSystemHealth` hook**

In `hooks/useSystemHealth.ts`. Calls `systemService.health()` on mount and then uses `usePolling` with a 30-second interval. Returns `{ health, isLoading, error, overallStatus }`. The `overallStatus` is computed: `'ok'` if all subsystems are `'ok'`, `'degraded'` if any is `'degraded'`, `'error'` if any is `'error'`.

**Task 55.2 — Build the `SubsystemCard` component**

In `components/system/SubsystemCard.tsx`. Receives a subsystem name, its icon (Lucide icons: `Database`, `Cpu`, `Cloud`, `Server`), status, and detail string. Renders a card with a colored left border: `3px solid` green/orange/red for ok/degraded/error respectively. Inside: the icon, subsystem name, a status badge (using the `Badge` component), and the detail string in small text.

**Task 55.3 — Build the `HealthGrid` and system page**

In `components/system/HealthGrid.tsx`. A simple 2×2 grid of `SubsystemCard` components. Also shows an overall status banner at the top: green with "All systems operational" or orange/red with the specific failing subsystem name.

In `app/system/page.tsx`, a Client Component using `useSystemHealth()`. Renders the page title "System Status" and the `HealthGrid`. Shows a `Spinner` on initial load. Add a "Refresh" button that re-calls the health endpoint immediately.

**Task 55.4 — Wire `SystemStatusDot` in `TopBar`**

Update `TopBar.tsx` to use `useSystemHealth()`. The dot changes color based on `overallStatus`. Add the same `Tooltip` wrapper showing "All systems operational" or "Degraded: [subsystem name]" on hover. Clicking the dot navigates to `/system`.

**Error Verification — Phase 55:**

With all systems running, verify the dot in the top bar is green. Navigate to `/system` and verify all four subsystem cards show `'ok'`. Stop Ollama (so Qwen is unavailable) and wait for the next 30-second poll — verify the dot turns orange and the Qwen card shows `'error'`. Verify clicking the dot navigates to `/system`.

**Phase 55 Checklist:**
- [x] `/system` page shows all four subsystem statuses
- [x] `SubsystemCard` left border color matches status
- [x] `SystemStatusDot` in TopBar updates every 30 seconds
- [x] Dot color correctly reflects worst-case subsystem status
- [x] Clicking the dot navigates to `/system`
- [x] "Refresh" button immediately re-polls the health endpoint
- [x] Overall status banner shows correct message

---

## Phase 56 — Final Polish: Animations, Error Boundaries, Performance Optimization, and End-to-End Validation

**Objective:** Add all remaining micro-interactions and page transitions, wrap the application in error boundaries, audit and fix all performance issues, and validate the complete end-to-end workflow.

**Technical Context:**

This phase is not about adding features — it is about making every existing feature feel polished and production-quality. The difference between a prototype and a great prototype is in these details: smooth page transitions, loading skeletons that match the real content shape, error states that are actionable, and a zero-console-error state.

**Page transitions** use Framer Motion's `AnimatePresence` with a shared `variants` pattern. Wrap the page content in a `<motion.div>` with `variants={{ initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } }}` and `transition={{ duration: 0.15 }}`. Add this to every page component. The exit animation is triggered by route changes in the App Router by wrapping the `children` in the root layout with `AnimatePresence mode="wait"`.

**Error Boundaries** catch JavaScript runtime errors in components and prevent the entire app from white-screening. Build `ErrorBoundary.tsx` as a class component (required by React's error boundary API) that catches errors and shows a friendly "Something went wrong" fallback with a "Reload" button. Wrap the root layout children, the chat area, and the document list separately with `ErrorBoundary`.

**Micro-Tasks:**

**Task 56.1 — Add page transition wrapper**

Create `components/shared/PageTransition.tsx` as a simple Framer Motion wrapper component. Every page file wraps its root element in `<PageTransition>`. Ensure `AnimatePresence mode="wait"` wraps the router's output in the root layout.

**Task 56.2 — Build the `ErrorBoundary` component**

In `components/shared/ErrorBoundary.tsx`. Class component with `state = { hasError: false, errorMessage: '' }`. `getDerivedStateFromError` sets `hasError: true`. `componentDidCatch` logs the error. Fallback renders a centered card with a `AlertCircle` icon, "Something went wrong" heading, the error message in small text, and a `window.location.reload()` button.

**Task 56.3 — Audit and fix all console warnings and errors**

Run `npm run build`. Fix every TypeScript error. Run the dev server and open DevTools. Verify zero console errors. Check for: missing `key` props in lists, `useEffect` missing dependency array entries, hydration mismatches, unhandled promise rejections. Fix all.

**Task 56.4 — Audit Tailwind token usage**

Do a global search for hardcoded hex colors (e.g., `#`, `rgb(`)) in component files. Replace every instance with the correct CSS variable from `tokens.css`. The only hardcoded colors allowed are in `tokens.css` itself. Verify that toggling between dark and light themes causes every element to update correctly.

**Task 56.5 — Add loading skeletons to workspace cards**

When `useWorkspaces()` is loading, instead of showing a spinner, show 3 skeleton workspace cards — `<div>` elements with the same dimensions as a real card but filled with shimmer placeholders. This pattern is "content-aware loading" and dramatically improves perceived performance.

**Task 56.6 — End-to-end validation**

Perform the following complete workflow without errors:

(1) Open `/workspaces` — verify skeleton cards appear briefly, then real cards load. Create a new workspace. Verify it appears in the sidebar immediately.

(2) Navigate to the new workspace's Documents tab. Upload a PDF. Watch status transition to Ready. Upload a DOCX. Watch both complete.

(3) Navigate to Chat. Verify `EmptyConversation` was shown before any messages. Type a query and submit. Verify optimistic message appears, thinking indicator shows, and a Markdown-formatted response appears with source citations. Submit 10 more queries. Verify conversation history scrolls correctly.

(4) Switch to Medium and Expert modes. Verify the mode changes and the model_used in the response footer reflects the correct model.

(5) Navigate to Analytics. Verify all metrics updated correctly.

(6) Navigate to System. Verify health report.

(7) Toggle dark/light theme throughout all pages and verify no visual regressions.

(8) Delete the workspace. Verify it disappears from the grid and sidebar and a second navigation attempt 404s.

**Task 56.7 — Performance audit**

Run `npm run build` and check the output bundle sizes. The `documents` and `chat` pages should not exceed 150KB of JavaScript. If any chunk is oversized, move large dependencies to dynamic imports: `const ReactMarkdown = dynamic(() => import('react-markdown'), { ssr: false })`. Apply `next/dynamic` with `loading: () => <Spinner />` to all heavy components (charts, Markdown renderer). Verify the Lighthouse Performance score in Chrome DevTools is above 85.

**Error Verification — Phase 56:**

`npm run build` must complete with zero errors and zero TypeScript errors. Open a private/incognito window (clears localStorage) and run the end-to-end workflow from Task 56.6. Zero console errors throughout. Theme toggle works on every page. All animations play smoothly at 60fps (check in Chrome DevTools Performance tab).

**Phase 56 Checklist:**
- [x] `npm run build` completes with zero TypeScript and build errors
- [x] Zero console errors in DevTools during complete end-to-end workflow
- [x] Page transitions animate smoothly between routes
- [x] `ErrorBoundary` catches and displays errors gracefully
- [x] All hardcoded colors replaced with CSS variable tokens
- [x] Skeleton loaders show on initial data fetch for workspace cards
- [x] Dark/light theme toggle produces zero visual regressions
- [x] All heavy components use `next/dynamic` for lazy loading
- [x] Lighthouse Performance score above 85
- [x] Complete workflow (create → upload → chat → analytics → delete) works without any error

---

## Milestone Summary

| Milestone | Phase | Completion Criterion |
|-----------|-------|---------------------|
| **M5-A** | Phase 47 | Navigation shell renders, routes work, theme toggles correctly |
| **M5-B** | Phase 49 | Document upload, status polling, and management works end-to-end |
| **M5-C** | Phase 52 | Full RAG chat pipeline working in the UI |
| **M5-D** | Phase 55 | Analytics and system health visible and real-time |
| **M5** | Phase 56 | Complete, polished, zero-error application |

---

## Cross-Cutting Rules for the Coding Agent

These rules are non-negotiable and apply to every single phase.

**Token Supremacy.** Every color, spacing, border-radius, shadow, and animation duration must reference a CSS variable from `tokens.css`. Search for any hardcoded hex value before marking a phase complete. The only exception: Framer Motion animation values, which can use numeric values.

**No UI Libraries.** Do not install or use shadcn/ui, Radix, Headless UI, MUI, Chakra, Mantine, or any other component library. Every component is hand-built. The reasoning: full visual control, no style overrides required, smaller bundle size, and zero dependency on external design systems.

**TypeScript Strictness.** All files are `.tsx` or `.ts`. `tsconfig.json` must have `"strict": true`. No `any` types except in the `ErrorBoundary` catch block. Run `tsc --noEmit` before completing each phase.

**CSS Variable Discipline.** Never use Tailwind color utilities (`text-gray-500`, `bg-slate-900`, `border-blue-400`) for color values. Tailwind is used only for layout utilities (`flex`, `grid`, `p-4`, `gap-2`, `overflow-hidden`, etc.). All colors go through `var(--...)` from `tokens.css`.

**Client/Server Component Boundary.** In Next.js App Router, components are Server Components by default. Only mark a component `"use client"` if it: uses `useState`, `useEffect`, `useRef`, event handlers, browser APIs (`localStorage`, `window`), or third-party libraries that require browser context. All data fetching that can be done server-side should be done server-side. The workspace layout fetches the workspace server-side; child Client Components read it from the Zustand store.

**Store Access Pattern.** Components read from Zustand stores using selector functions, not the entire store: `const workspaces = useWorkspaceStore(state => state.workspaces)`. This prevents unnecessary re-renders when unrelated store slices update.

**Error Handling Pattern.** Every `async` function that calls the API service layer must be wrapped in `try/catch`. The catch block receives an `ApiError` instance. Always show the `ApiError.detail` string (not the raw `Error.message`) to the user — backend detail messages are user-friendly by design. Never swallow errors silently.

**Polling Cleanup.** Every `usePolling` call that creates a `setInterval` must be cleaned up by returning a cleanup function from `useEffect`. Failing to do so causes memory leaks and stale closures that produce incorrect data after navigation.

**Phase Completion Gate.** Before marking any checklist item as done, manually verify the specific behavior described. A phase is complete only when every item is checked. If a later phase reveals a bug in an earlier phase, go back, fix the root cause, and re-verify the affected phase's checklist before proceeding.