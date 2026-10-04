from backend.models.context import ContextPackage
from backend.models.chat import RetrievedChunk

class PromptBuilder:
    """
    Advanced Prompt & Context Engineering Builder for Pedagogical RAG.
    Harnesses both small local models (Ollama 3B/7B) and high-speed cloud models (Groq)
    to deliver structured, hallucination-free, high-utility educational responses.
    """

    def build_from_context(self, context: ContextPackage) -> list[dict]:
        is_oob = getattr(context, 'is_out_of_box', False)
        has_evidence = bool(context.retrieved_chunks and len(context.retrieved_chunks) > 0) and not is_oob
        
        system_prompt = self.build_system_prompt(context.mode, has_evidence, is_oob)
        response_rules = self.format_response_rules(
            mode=context.mode,
            confidence_level=context.confidence.level,
            has_evidence=has_evidence,
            workspace_summary=context.workspace_summary,
            is_out_of_box=is_oob,
            uncovered_topics=getattr(context, 'uncovered_topics', []),
            query=context.query
        )
        
        # Construct prompt ensuring the static parts are at the very top (prefix)
        # to maximize LLM Prompt Caching hits.
        parts = [
            system_prompt,
            response_rules
        ]
        
        # Workspace summary changes rarely, so it comes next in the cache hierarchy
        if context.workspace_summary:
            parts.append(f"=== Workspace Knowledge & Context ===\n{context.workspace_summary}")

        # User memory profile — injected BEFORE dynamic evidence for LLM cache hits
        if getattr(context, 'memory_profile_snippet', ''):
            parts.append(
                f"=== User Learning Profile (This Workspace) ===\n"
                f"{context.memory_profile_snippet}"
            )

        # Workspace-wide cross-session memory bank (epistemic history across all conversations)
        if getattr(context, 'workspace_memory_bank', ''):
            parts.append(
                f"=== Workspace Cross-Session Memory & Activity ===\n"
                f"{context.workspace_memory_bank}"
            )

        # RAG Evidence (retrieved chunks from uploaded documents)
        if has_evidence:
            evidence = self.format_retrieved_evidence(context.retrieved_chunks)
            parts.append(evidence)
        elif is_oob:
            uncovered_str = ", ".join(getattr(context, 'uncovered_topics', [])) or context.query
            parts.append(
                f"=== Workspace Document Context (Out-of-Box Fallback) ===\n"
                f"[The uploaded workspace documents were examined, but they DO NOT contain information or chapters covering '{uncovered_str}'.\n"
                f"Do NOT invent or use snippet citation brackets like [1] or [2].\n"
                f"You MUST educate the user on '{context.query}' using foundational academic science curriculum principles,\n"
                f"beginning with the mandatory out-of-box callout note.]"
            )
        else:
            parts.append(
                "=== Workspace Document Evidence ===\n"
                "[No relevant document chunks matched for this specific query. "
                "Synthesize a comprehensive, high-quality pedagogical explanation using foundational academic principles.]"
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
        
    def build_system_prompt(self, mode: str, has_evidence: bool, is_out_of_box: bool = False) -> str:
        base = (
            "You are an expert academic tutor, educational architect, and research intelligence mentor "
            "designed to help students and researchers master complex concepts rapidly through structured, clear, and rigorous explanations."
        )
        if has_evidence:
            base += (
                "\nYour primary objective is to ground your analysis directly in the provided workspace document evidence, "
                "citing exact snippets to maintain 100% academic integrity and zero hallucination."
            )
        elif is_out_of_box:
            base += (
                "\nThe user is inquiring about a topic not present in their uploaded workspace documents. "
                "Your objective is to provide a complete, authoritative pedagogical explanation from first principles "
                "while clearly noting that this information comes from foundational academic curriculum (out-of-box context)."
            )
        else:
            base += (
                "\nWhen no specific workspace document snippets match, use your broad academic and scientific knowledge "
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
        
    def format_response_rules(
        self,
        mode: str,
        confidence_level: str,
        has_evidence: bool,
        workspace_summary: str = "",
        is_out_of_box: bool = False,
        uncovered_topics: list[str] | None = None,
        query: str = ""
    ) -> str:
        rules = ["=== Pedagogical Formatting & Grounding Rules ==="]
        uncovered_topics = uncovered_topics or []
        
        # 1. Grounding & Anti-Hallucination Rules
        if has_evidence:
            rules.append("- Document Grounding: Workspace documents are uploaded and active. Carefully analyze the provided snippets.")
            rules.append("- Zero-Hallucination Mandate: Do NOT state that 'no documents exist' or that 'no workspace files are available'. Base your response directly on the provided snippets.")
            rules.append("- Source Citations: Cite your sources using bracketed numbers corresponding to the snippet, e.g. [1], [2].")
            rules.append("- Strict Negative Constraint: Do not invent page numbers, authors, or quotes not present in the snippets.")
            rules.append("- Lesson / Curriculum Requests: If the user asks to list lesson names, chapters, or syllabus topics, extract and enumerate EVERY chapter/lesson listed in the snippets under its respective Unit, stating the chapter number and full title.")
            rules.append("- User Query History & Learning Reflection: If the user is asking about their past questions, asked topics, weak areas, or learning progress, structure your response to clearly list all their past questions chronologically with session names/dates from the workspace history snippet, summarize their active topics, and give constructive learning recommendations.")
        elif is_out_of_box:
            topic_hint = ", ".join(uncovered_topics) if uncovered_topics else "the requested subject"
            rules.append("- Out-of-Box Context Hybridization Policy (CRITICAL):")
            rules.append(f"  * The user is inquiring about '{query}', which is NOT covered in the uploaded workspace documents.")
            rules.append("  * DO NOT refuse to answer the user's question, and DO NOT talk about unrelated chapters.")
            rules.append("  * DO NOT generate bracketed snippet citations like [1] or [2].")
            rules.append("  * You MUST thoroughly educate the user on the requested topic using your broad, foundational academic science knowledge.")
            rules.append("  * MANDATORY CALLOUT: Your response MUST begin with this exact blockquote format at the very top of your output:")
            rules.append(f"    > **Note**: *Content not from uploaded content.* The uploaded workspace documents do not contain coverage of **{topic_hint}**. The following explanation is provided using foundational academic biology curriculum principles:")
            rules.append("  * Follow this notice immediately with an in-depth, structured educational breakdown answering the user's query.")
        else:
            if workspace_summary and "Uploaded Workspace Files" in workspace_summary and "None" not in workspace_summary:
                rules.append("- Document Scope: Workspace files are uploaded, but no direct semantic chunk matched this specific prompt. Synthesize your answer using core academic knowledge while acknowledging the uploaded subject matter.")
            else:
                rules.append("- Evidence Scope: No workspace document snippets matched. Answer directly using foundational scientific/academic knowledge.")
            rules.append("- Negative Constraint: Do NOT generate artificial snippet citation brackets like [1] or [2] when no documents were retrieved.")

        # Check for Diagram / Visual Request
        q_lower = query.lower() if query else ""
        if any(w in q_lower for w in ["diagram", "diagrams", "flowchart", "drawing", "illustration", "pathway"]):
            rules.append("- Visual / Diagram Instruction:")
            rules.append("  * The user explicitly requested diagrams or illustrations.")
            rules.append("  * In your explanation, provide a detailed, beautifully aligned ASCII flowchart or diagram illustrating the anatomical pathways, organ relationships, and functional mechanisms (e.g. Alimentary canal sequence from Mouth to Anus with secretions and enzymatic actions).")

        # 2. Structural Scaffolding for Learning
        if mode == "expert":
            rules.append("- Use rich, structured Markdown with the following mandatory sections:")
            rules.append("  1. `### Core Concept / Summary`: 2-3 sentence intuitive overview of the topic or physiological purpose.")
            rules.append("  2. `### Detailed Breakdown & Mechanisms`: In-depth breakdown with bullet points, numbered stages, and **bold key terms**.")
            if has_evidence:
                rules.append("  3. `### Document Evidence & Analysis`: Deep dive grounded in the retrieved snippets with citations.")
            else:
                rules.append("  3. `### Scientific / Conceptual Deep Dive & Visual Pathway`: Deeper theoretical explanation, enzymatic pathways, and ASCII diagrams/flowcharts.")
            rules.append("  4. `### Key Takeaways & Review Points`: 3-5 concise bullet points for rapid memorization and research review.")
            rules.append("- Use tables, code blocks, or ASCII diagrams whenever comparing concepts or showing technical processes.")
            
        elif mode == "medium":
            rules.append("- Structure your response clearly with Markdown:")
            rules.append("  1. `### Core Concept`: Quick, clear summary.")
            rules.append("  2. `### Key Mechanisms & Anatomical Breakdown`: Numbered or bulleted points breaking down the essential mechanics and pathways.")
            rules.append("  3. `### Key Takeaways`: Summary bullet points for quick retention.")
            if has_evidence:
                rules.append("- Cite sources using bracketed numbers [1], [2].")
                
        else:  # local / fast
            rules.append("- Provide a thorough, direct explanation structured with clear bullet points and bold headers.")
            rules.append("- Avoid 1-line superficial answers; explain the 'why' and 'how' behind the concept.")
            if has_evidence:
                rules.append("- Include bracketed citations [1] for evidence-backed points.")
                
        # 3. Universal Markdown Table Formatting Rules
        rules.append("- Markdown Table Rules:")
        rules.append("  * Keep every table row strictly on a single line starting and ending with '|'.")
        rules.append("  * Every row MUST have the EXACT same number of columns as the header.")
        rules.append("  * Do NOT place raw newlines or extra '|' delimiters inside a table cell. Use `<br /> • ` to separate multiple bullet points inside a single cell (e.g. `| 1 | Air Pollution | • Acid rain <br /> • Ozone depletion | [1] |`).")

        return "\n".join(rules)
