import os
import json
from typing import List, Dict, Any, Optional
from src.models.pydantic_schemas import ModuleNode
import openai # Using standard OpenAI client, assuming compatible endpoint or wrapper

class ContextWindowBudget:
    def __init__(self, limit: int = 128000):
        self.limit = limit
        self.usage = 0

    def track(self, tokens: int):
        self.usage += tokens

    def can_afford(self, tokens: int) -> bool:
        return (self.usage + tokens) <= self.limit

class Semanticist:
    def __init__(self, model_bulk: str = "gpt-4o-mini", model_synth: str = "gpt-4o"):

        self.model_bulk = model_bulk
        self.model_synth = model_synth
        self.budget = ContextWindowBudget()
        # Lazy initialization or guarded
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def generate_purpose_statement(self, module_content: str) -> str:
        if not self.client:
            return "Purpose statement skipped (No API key provided)."
        try:
            response = self.client.chat.completions.create(
                model=self.model_bulk,
                messages=[
                    {"role": "system", "content": "Explain the business purpose of this code in 2-3 sentences. Focus on what it does, not how."},
                    {"role": "user", "content": module_content}
                ]
            )
            purpose = response.choices[0].message.content
            return purpose
        except Exception as e:
            return f"Error generating purpose: {e}"

    def cluster_into_domains(self, modules: List[ModuleNode]) -> List[ModuleNode]:
        """
        Uses embeddings to cluster modules. (Placeholder for actual scikit-learn implementation)
        """
        # 1. Get embeddings for each purpose statement
        # 2. Run K-Means
        # 3. Assign domain labels
        return modules

    def answer_day_one_questions(self, context: str) -> str:
        if not self.client:
            return "Day-One questions skipped (No API key provided)."
        try:
            response = self.client.chat.completions.create(

                model=self.model_synth,
                messages=[
                    {"role": "system", "content": "Answer the Five FDE Day-One Questions based on the provided architectural context. Provide evidence citations."},
                    {"role": "user", "content": context}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error answering questions: {e}"
