# CATALYST — Query Understanding Solution

### Core Problem

**Bad user spelling → bad retrieval → no answer.**

Don't solve this with one large NLP model.

### Recommended Architecture

```text
User Query
    ↓
Normalize
    ↓
Corpus-Aware Spelling Recovery
    ↓
Context + Intent Understanding
    ↓
Canonical Query
    ↓
 ┌──────────────┬──────────────┐
 ↓              ↓
Dense Search   BM25 Search
 ↓              ↓
 └─────── RRF Fusion ─────────┘
             ↓
         Reranker
             ↓
       Evidence Check
        ↓          ↓
     Strong       Weak
        ↓          ↓
       LLM      Reformulate
                   ↓
              Retry Retrieval
```

### 1. Corpus-Aware Spelling

Don't rely only on a dictionary.

```text
photoynthesis
      ↓
Uploaded PDF vocabulary
      ↓
photosynthesis
```

Use:

* **SymSpell** → fast candidate generation
* **RapidFuzz** → similarity scoring
* **Document vocabulary** → domain authority
* **n-grams** → technical phrases

---

### 2. Never Trust Correction Alone

Keep the original query.

```text
Original Query
+
Corrected Query
```

Search both.

This prevents a wrong correction from destroying retrieval.

---

### 3. Hybrid Retrieval

Don't use vector search alone.

```text
Dense → meaning
BM25  → exact words / spelling
RRF   → combine both
```

This makes retrieval much more typo-resistant.

---

### 4. Context Understanding

For:

> "Explain mitochondria."

Then:

> "What does it produce?"

Resolve to:

> "What does mitochondria produce?"

Maintain:

```text
active document
active chapter
current topic
recent entities
previous query
```

---

### 5. Adaptive Query Reformulation

**Don't rewrite every query.**

```text
Easy query
→ Direct retrieval

Weak retrieval
→ Query expansion

Still weak
→ Local LLM reformulation

Still no evidence
→ Abstain
```

This keeps the system fast.

---

### 6. Reranking

Retrieve many → rank carefully.

```text
Dense + BM25
      ↓
Top 20–50
      ↓
Reranker
      ↓
Top 5–10
      ↓
LLM
```

The LLM should receive **high-quality evidence**, not raw retrieval results.

---

### 7. No-Hallucination Rule

```text
Evidence exists
    ↓
Generate answer
```

```text
Evidence insufficient
    ↓
Recover query
    ↓
Retry
    ↓
Still insufficient
    ↓
"I couldn't find enough evidence."
```

**Never let the LLM guess.**

---

# Production Stack

| Problem               | Solution             |
| --------------------- | -------------------- |
| Typo                  | SymSpell             |
| Fuzzy term            | RapidFuzz            |
| Domain terminology    | Document Lexicon     |
| Phrase recovery       | n-grams              |
| Meaning               | Dense retrieval      |
| Exact terminology     | BM25                 |
| Combination           | RRF                  |
| Precision             | Reranker             |
| Context               | Conversation state   |
| Difficult queries     | Local query rewriter |
| Hallucination control | Evidence gate        |
| Unknown answer        | Abstention           |

## Sharp Principle

> **Don't build a smarter spell-checker. Build a retrieval system that survives bad language.**

Your core CATALYST pipeline should be:

**`Corpus-Aware NLP → Hybrid Retrieval → Reranking → Evidence Gate → Grounded LLM`**
