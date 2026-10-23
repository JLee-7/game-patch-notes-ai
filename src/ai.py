"""AI summarization and chat helpers using any OpenAI-compatible endpoint."""

import os
from typing import Optional
from openai import OpenAI


class AIClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def summarize_patch(self, title: str, contents: str) -> str:
        if not contents.strip():
            return "No content available to summarize."

        prompt = f"""You are a sharp gaming analyst. Summarize this patch notes entry.

Title: {title}

Raw notes:
{contents[:12000]}

Write a clean, useful summary that covers:
- What changed (features, balance, maps, bugs)
- Notable buffs, nerfs, or new additions
- Anything players should care about

Keep concise but informative. Use bullet points. No fluff."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI summary failed: {e}"

    def chat_about_patch(self, patch_context: str, user_question: str, history: list = None) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful gaming assistant. Answer questions about the provided patch notes accurately. If the notes don't contain the answer, say so.",
            },
            {
                "role": "user",
                "content": f"Here are the patch notes:\n\n{patch_context[:15000]}\n\nQuestion: {user_question}",
            },
        ]
        if history:
            messages = messages[:1] + history + messages[1:]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=600,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Chat failed: {e}"
