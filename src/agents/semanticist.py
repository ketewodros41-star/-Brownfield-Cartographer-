import os
import json
import ast
from typing import List, Dict, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from src.models.pydantic_schemas import ModuleNode
import openai # Using standard OpenAI client, assuming compatible endpoint or wrapper

class ContextWindowBudget:
    def __init__(self, limit: int = 128000):
        self.limit = limit
        self.usage = 0
        self.cost_usd = 0.0

    def track(self, tokens: int, model: str, pricing: Dict[str, float]):
        self.usage += tokens
        price_per_1k = pricing.get(model, 0.0)
        self.cost_usd += (tokens / 1000.0) * price_per_1k

    def can_afford(self, tokens: int) -> bool:
        return (self.usage + tokens) <= self.limit

    def summary(self) -> Dict[str, Any]:
        return {"tokens": self.usage, "cost_usd": round(self.cost_usd, 6), "limit": self.limit}

class Semanticist:
    def __init__(self, model_bulk: str = "gpt-4o-mini", model_synth: str = "gpt-4o"):

        self.model_bulk = model_bulk
        self.model_synth = model_synth
        self.budget = ContextWindowBudget()
        # Lazy initialization or guarded
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434/v1")
        self.use_ollama = os.environ.get("USE_OLLAMA", "").lower() in ("true", "1", "yes")

        self.client = None
        self.embed_client = None
        self.provider = "none"

        if self.use_ollama:
            self.client = openai.OpenAI(
                base_url=self.ollama_host,
                api_key="ollama" # Required by client but ignored by Ollama
            )
            self.provider = "ollama"
            self.model_bulk = os.environ.get("OLLAMA_MODEL_BULK", "llama3")
            self.model_synth = os.environ.get("OLLAMA_MODEL_SYNTH", "llama3")
        elif self.groq_key:
            # Use Groq's OpenAI-compatible endpoint for chat
            self.client = openai.OpenAI(
                api_key=self.groq_key,
                base_url="https://api.groq.com/openai/v1",
            )
            self.provider = "groq"
            # Allow model override via env
            self.model_bulk = os.environ.get("GROQ_MODEL_BULK", "llama-3.1-8b-instant")
            self.model_synth = os.environ.get("GROQ_MODEL_SYNTH", "llama-3.1-70b-versatile")
        elif self.openai_key:
            self.client = openai.OpenAI(api_key=self.openai_key)
            self.provider = "openai"

        # Embeddings still require OpenAI for now (Ollama embeddings not yet hooked up)
        if self.openai_key:
            self.embed_client = openai.OpenAI(api_key=self.openai_key)

        self.embedding_model = "text-embedding-3-small"
        # Approximate USD cost per 1K tokens (single-rate for estimation).
        self.model_pricing = {
            "gpt-4o-mini": 0.00015,
            "gpt-4o": 0.005,
            "text-embedding-3-small": 0.00002,
            # Groq or unknown models default to 0 unless provided.
            "llama-3.1-8b-instant": 0.0,
            "llama-3.1-70b-versatile": 0.0,
        }

    def generate_purpose_statement(self, module_content: str) -> str:
        if not self.client:
            return "Purpose statement skipped (No API key provided)."

        stripped = self._strip_docstrings(module_content)
        prompt = (
            "You are analyzing source code. Ignore all docstrings and comments. "
            "Derive the business purpose from implementation details only. "
            "Write 2-3 sentences describing what the module does (not how)."
        )
        try:
            response = self._chat(
                model=self.model_bulk,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": stripped},
                ],
            )
            purpose = response.choices[0].message.content
            return purpose
        except Exception as e:
            return f"Error generating purpose: {e}"

    def get_embeddings_for_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        embeddings = self._get_embeddings(texts)
        if embeddings is None:
            return None
        return embeddings.tolist()

    def detect_docstring_drift(self, module_content: str, purpose_statement: str) -> Dict[str, Any]:
        """
        Compare docstring intent vs implementation-derived purpose.
        Returns structured output with severity and contradictions.
        """
        docstring = self._extract_docstring(module_content)
        if not docstring:
            return {"severity": "none", "contradictions": [], "note": "no_docstring"}

        if not self.client:
            # Heuristic fallback: flag if docstring is empty or overly short
            if len(docstring.strip()) < 20:
                return {"severity": "low", "contradictions": [], "note": "short_docstring"}
            return {"severity": "none", "contradictions": [], "note": "llm_unavailable"}

        system = (
            "Compare the module docstring to the implementation-derived purpose. "
            "Return JSON with keys: severity (none|low|medium|high), contradictions (list of strings), summary."
        )
        user = json.dumps({
            "docstring": docstring,
            "purpose_statement": purpose_statement
        })
        try:
            response = self._chat(
                model=self.model_synth,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            content = response.choices[0].message.content
            return self._safe_json(content)
        except Exception as e:
            return {"severity": "unknown", "contradictions": [], "summary": f"error: {e}"}

    def cluster_into_domains(self, modules: List[ModuleNode]) -> List[ModuleNode]:
        """
        Uses embeddings to cluster modules into inferred domains.
        """
        # 1. Get embeddings for each purpose statement
        texts = [m.purpose_statement or "" for m in modules]
        if not any(texts):
            return modules

        embeddings = self._get_embeddings(texts)
        if embeddings is None:
            return modules

        # 2. Run K-Means (k inferred from sqrt(n))
        n = len(embeddings)
        k = max(2, int(np.sqrt(n)))
        k = min(k, n)
        if k <= 1:
            return modules

        km = KMeans(n_clusters=k, n_init="auto", random_state=42)
        labels = km.fit_predict(embeddings)

        # 3. Assign domain labels using top TF-IDF terms per cluster
        vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
        tfidf = vectorizer.fit_transform(texts)
        terms = np.array(vectorizer.get_feature_names_out())

        for cluster_id in range(k):
            idxs = np.where(labels == cluster_id)[0]
            if len(idxs) == 0:
                continue
            cluster_tfidf = tfidf[idxs].mean(axis=0)
            top_idx = np.asarray(cluster_tfidf).ravel().argsort()[-3:][::-1]
            top_terms = [t for t in terms[top_idx] if t]
            label = "domain:" + ("-".join(top_terms) if top_terms else f"cluster-{cluster_id}")
            for i in idxs:
                modules[i].domain_cluster = label
        return modules

    def answer_day_one_questions(self, context: Dict[str, Any]) -> str:
        if not self.client:
            return self._fallback_day_one_answers(context)

        system = (
            "Answer the Five FDE Day-One Questions using the provided evidence. "
            "Cite each claim with file path and line range. "
            "Include analysis method tag (static|llm)."
        )
        try:
            response = self._chat(
                model=self.model_synth,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(context)},
                ],
            )
            content = response.choices[0].message.content
            return self._ensure_citations(content, context)
        except Exception as e:
            return f"Error answering questions: {e}"

    def _get_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        if not self.embed_client:
            return None
        total_tokens = sum(self._estimate_tokens(t) for t in texts)
        if not self.budget.can_afford(total_tokens):
            return None
        try:
            response = self.embed_client.embeddings.create(
                model=self.embedding_model,
                input=texts,
            )
            self.budget.track(total_tokens, self.embedding_model, self.model_pricing)
            vectors = [d.embedding for d in response.data]
            return np.array(vectors)
        except Exception:
            return None

    def _chat(self, model: str, messages: List[Dict[str, str]]):
        total_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in messages)
        if not self.budget.can_afford(total_tokens):
            raise RuntimeError("Token budget exceeded.")
        response = self.client.chat.completions.create(model=model, messages=messages)
        self.budget.track(total_tokens, model, self.model_pricing)
        return response

    def _estimate_tokens(self, text: str) -> int:
        # Rough heuristic: 1 token ~= 4 chars
        return max(1, int(len(text) / 4))

    def _strip_docstrings(self, source: str) -> str:
        try:
            tree = ast.parse(source)
        except Exception:
            return source

        class DocstringStripper(ast.NodeTransformer):
            def _strip(self, node):
                if hasattr(node, "body") and node.body:
                    first = node.body[0]
                    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                        node.body = node.body[1:]
                return node

            def visit_Module(self, node):
                return self._strip(node)

            def visit_FunctionDef(self, node):
                self.generic_visit(node)
                return self._strip(node)

            def visit_AsyncFunctionDef(self, node):
                self.generic_visit(node)
                return self._strip(node)

            def visit_ClassDef(self, node):
                self.generic_visit(node)
                return self._strip(node)

        stripped = DocstringStripper().visit(tree)
        return ast.unparse(stripped) if hasattr(ast, "unparse") else source

    def _extract_docstring(self, source: str) -> str:
        try:
            tree = ast.parse(source)
        except Exception:
            return ""
        return ast.get_docstring(tree) or ""

    def _safe_json(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            return {"severity": "unknown", "contradictions": [], "summary": content}

    def _ensure_citations(self, content: str, context: Dict[str, Any]) -> str:
        if "evidence:" in content.lower():
            return content
        evidence_lines = []
        for ev in context.get("evidence", {}).get("modules", []):
            file = ev.get("file", "")
            lr = ev.get("line_range", [1, 1])
            method = ev.get("method", "static")
            evidence_lines.append(f"- {file}:{lr[0]}-{lr[1]} (method: {method})")
        for ev in context.get("evidence", {}).get("lineage", []):
            file = ev.get("file", "")
            lr = ev.get("line_range", [1, 1])
            method = ev.get("method", "static")
            evidence_lines.append(f"- {file}:{lr[0]}-{lr[1]} (method: {method})")
        appendix = "\n\nEvidence:\n" + "\n".join(evidence_lines[:20])
        return content + appendix

    def _fallback_day_one_answers(self, context: Dict[str, Any]) -> str:
        overview = context.get("overview", "N/A")
        critical = context.get("critical_path", [])
        sources = context.get("data_sources", [])
        sinks = context.get("data_sinks", [])
        tech_debt = context.get("tech_debt", [])
        high_velocity = context.get("high_velocity", [])

        lines = []
        lines.append("Q1: What does this system do at a high level?")
        lines.append(f"{overview}")
        lines.append("")
        lines.append("Q2: What are the most critical modules?")
        lines.extend(critical or ["None identified."])
        lines.append("")
        lines.append("Q3: What are the primary data sources and sinks?")
        lines.append("Sources:")
        lines.extend(sources or ["None identified."])
        lines.append("Sinks:")
        lines.extend(sinks or ["None identified."])
        lines.append("")
        lines.append("Q4: Where is the technical debt or risk?")
        lines.extend(tech_debt or ["None identified."])
        lines.append("")
        lines.append("Q5: What changes frequently and should be watched closely?")
        lines.extend(high_velocity or ["None identified."])

        content = "\n".join(lines)
        return self._ensure_citations(content, context)
