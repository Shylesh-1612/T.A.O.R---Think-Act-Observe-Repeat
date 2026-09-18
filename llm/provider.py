import os
import time
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from google import genai

from llm.base import LLMBase

load_dotenv(".env", override=True)


class GeminiProvider(LLMBase):

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing from .env"
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate(
        self,
        messages: List[Dict[str, str]],
        response_schema: Optional[Any] = None
    ) -> str:

        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            prompt_parts.append(
                f"{role}: {content}"
            )

        prompt = "\n".join(prompt_parts)

        last_error = None

        for attempt in range(3):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text

            except Exception as e:

                last_error = e
                error_text = str(e)

                temporary_errors = (
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "INTERNAL"
                )

                if any(
                    err in error_text
                    for err in temporary_errors
                ):

                    if attempt < 2:

                        if (
                            "429" in error_text
                            or "RESOURCE_EXHAUSTED" in error_text
                        ):
                            wait_time = 30
                        else:
                            wait_time = 2 ** attempt

                        print(
                            f"Gemini temporary error. "
                            f"Retrying in {wait_time}s..."
                        )

                        time.sleep(wait_time)

                        continue

                break

        raise RuntimeError(
            f"Gemini API Error after retries: {last_error}"
        ) from last_error