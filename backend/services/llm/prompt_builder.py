from backend.models.context import ContextPackage
from backend.models.chat import RetrievedChunk

class PromptBuilder:
    """
    Advanced Prompt & Context Engineering Builder for Pedagogical RAG.
    Harnesses both small local models (Ollama 3B/7B) and high-speed cloud models (Groq)
    to deliver structured, hallucination-free, high-utility educational responses.
    """

    def build_from_context(self, context: ContextPackage) -> list[dict]:
        has_evidence = bool(context.retrieved_chunks and context.confidence.level != "LOW")
        
        system_prompt = self.build_system_prompt(context.mode, has_evidence)
        response_rules = self.format_response_rules(context.mode, context.confidence.level, has_evidence)
        
        # Construct prompt ensuring the static parts are at the very top (prefix)
        # to maximize LLM Prompt Caching hits.
        parts = [
            system_prompt,
            response_rules
        ]
        
        # Workspace summary changes rarely, so it comes next in the cache hierarchy
        if context.workspace_summary:
            parts.append(f"=== Workspace Knowledge & Context ===\n{context.workspace_summary}")
            
        # RAG Evidence (retrieved chunks from uploaded documents)
        if has_evidence:
            evidence = self.format_retrieved_evidence(context.retrieved_chunks)
            parts.append(evidence)
        else:
            parts.append(
                "=== Workspace Document Evidence ===\n"
                "[No relevant documents matched in workspace for this specific query. "
                "Synthesize a comprehensive, high-quality pedagogical explanation using foundational academic knowledge.]"
            )
        
        # Dynamic chat history
        if context.recent_messages:
            formatted_history = []
            for msg in context.recent_messages:
                role = "Student/User" if msg["role"] == "user" else "Assistant/Mentor"
                formatted_history.append(f"{role}: {msg['message']}")
            parts.append("=== Recent Conversation History ===\n" + "\n".join(formatted_history))
            
        full_system = "\n\n".join(parts)
        
        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": context.query}
        ]
        
        return messages
        
    def build_system_prompt(self, mode: str, has_evidence: bool) -> str:
        base = (
            "You are an expert academic tutor and research intelligence mentor designed to help students "
            "and researchers master complex concepts rapidly through structured, clear, and rigorous explanations."
        )
        if has_evidence:
            base += (
                "\nYour primary objective is to ground your analysis directly in the provided workspace document evidence, "
                "citing exact snippets to maintain 100% academic integrity and zero hallucination."
            )
        else:
            base += (
                "\nWhen no workspace document evidence is provided, use your broad academic and scientific knowledge "
                "to provide an exhaustive, clear, step-by-step breakdown from first principles."
            )
        return f"=== System Persona & Role ===\n{base}"
        
    def format_retrieved_evidence(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "=== Retrieved Document Evidence ===\nNo evidence available."
            
        parts = ["=== Retrieved Document Evidence ==="]
        for i, chunk in enumerate(chunks):
            header = f"Snippet [{i+1}]"
            meta_parts = []
            if chunk.source_file:
                meta_parts.append(f"File: {chunk.source_file}")
            if chunk.page_number:
                meta_parts.append(f"Page: {chunk.page_number}")
            if chunk.section_heading:
                meta_parts.append(f"Section: {chunk.section_heading}")
                
            if meta_parts:
                header += f" ({', '.join(meta_parts)})"
            parts.append(f"{header}:\n{chunk.chunk_text.strip()}")
            
        return "\n\n".join(parts)
        
    def format_response_rules(self, mode: str, confidence_level: str, has_evidence: bool) -> str:
        rules = ["=== Pedagogical Formatting & Grounding Rules ==="]
        
        # 1. Grounding & Hallucination Rules
        if has_evidence:
            if confidence_level == "MEDIUM":
                rules.append("- Evidence Scope: Moderate evidence found in uploaded files. Base your core facts strictly on the snippets, and note where details are omitted.")
            else:
                rules.append("- Evidence Scope: High-confidence evidence found. Ground all key claims in the provided snippets.")
            rules.append("- Source Citations: Cite your sources using bracketed numbers corresponding to the snippet, e.g. [1], [2].")
            rules.append("- Strict Negative Constraint: Do not invent page numbers, authors, or quotes not present in the snippets.")
        else:
            rules.append("- Evidence Scope: No workspace document snippets matched. Answer directly using foundational scientific/academic knowledge.")
            rules.append("- Transparency: Clearly state that this explanation is based on general academic principles.")
            rules.append("- Negative Constraint: Do NOT generate artificial snippet citation brackets like [1] or [2] when no documents were retrieved.")

        # 2. Structural Scaffolding for Learning
        if mode == "expert":
            rules.append("- Use rich, structured Markdown with the following mandatory sections:")
            rules.append("  1. `### 🎯 Core Concept / Summary`: 2-3 sentence intuitive overview of the topic.")
            rules.append("  2. `### 📖 Step-by-Step Breakdown & Mechanism`: In-depth breakdown with bullet points, numbered mechanisms, and **bold key terms**.")
            if has_evidence:
                rules.append("  3. `### 🔬 Document Evidence & Analysis`: Deep dive grounded in the retrieved snippets with citations.")
            else:
                rules.append("  3. `### 🔬 Scientific / Conceptual Deep Dive`: Deeper theoretical explanation, practical analogies, or mathematical formulations.")
            rules.append("  4. `### 💡 Key Takeaways & Review Points`: 3-5 concise bullet points for rapid memorization and research review.")
            rules.append("- Use tables, code blocks, or ASCII diagrams whenever comparing concepts or showing technical processes.")
            
        elif mode == "medium":
            rules.append("- Structure your response clearly with Markdown:")
            rules.append("  1. `### 🎯 Core Concept`: Quick, clear summary.")
            rules.append("  2. `### 📖 Key Mechanisms & Breakdown`: Numbered or bulleted points breaking down the essential mechanics.")
            rules.append("  3. `### 💡 Key Takeaways`: Summary bullet points for quick retention.")
            if has_evidence:
                rules.append("- Cite sources using bracketed numbers [1], [2].")
                
        else:  # local / fast
            rules.append("- Provide a thorough, direct explanation structured with clear bullet points and bold headers.")
            rules.append("- Avoid 1-line superficial answers; explain the 'why' and 'how' behind the concept.")
            if has_evidence:
                rules.append("- Include bracketed citations [1] for evidence-backed points.")
                
        return "\n".join(rules)
