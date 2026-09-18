import time
import httpx
from typing import Dict, Any
from urllib.parse import urlencode

from .base import Tool


class WebSearch(Tool):
    name = "web_search"
    description = (
        "Searches the web for current information using Wikipedia. "
        "Good for general knowledge, facts, and events."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }

    # Simple in-memory cache
    _cache = {}

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "").strip()

        if not query:
            return {
                "status": "error",
                "error_type": "invalid_input",
                "message": "Missing query"
            }

        # Avoid repeatedly hitting Wikipedia with the same query
        cache_key = query.lower()

        if cache_key in self._cache:
            return {
                "status": "success",
                "tool": self.name,
                "data": {
                    "results": self._cache[cache_key],
                    "cached": True
                }
            }

        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,
            "utf8": 1,
            "format": "json",
            "maxlag": 5
        }

        # Replace this with a real contact address if you have one.
        headers = {
            "User-Agent": (
                "NexusAgent/1.0 "
                "(https://github.com/yourusername/nexus-agent; "
                "your-email@example.com)"
            )
        }

        try:
            with httpx.Client(
                headers=headers,
                timeout=10.0,
                follow_redirects=True
            ) as client:

                for attempt in range(3):

                    response = client.get(
                        url,
                        params=params
                    )

                    # Wikimedia says clients should respect Retry-After
                    if response.status_code == 429:

                        retry_after = response.headers.get(
                            "Retry-After"
                        )

                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except ValueError:
                                wait_time = 5.0
                        else:
                            # Exponential backoff
                            wait_time = 5 * (2 ** attempt)

                        if attempt < 2:
                            time.sleep(min(wait_time, 30))
                            continue

                        return {
                            "status": "warning",
                            "tool": self.name,
                            "error_type": "rate_limited",
                            "message": (
                                "Wikipedia rate limit reached. "
                                f"Retry after approximately {wait_time:.0f} seconds."
                            )
                        }

                    response.raise_for_status()

                    data = response.json()

                    # Handle MediaWiki API-level errors
                    if "error" in data:
                        error = data["error"]

                        return {
                            "status": "error",
                            "tool": self.name,
                            "error_type": "api_error",
                            "message": error.get(
                                "info",
                                "Wikipedia API returned an error."
                            )
                        }

                    results = data.get(
                        "query", {}
                    ).get(
                        "search", []
                    )

                    if not results:
                        return {
                            "status": "success",
                            "tool": self.name,
                            "data": {
                                "results": [],
                                "message": "No results found"
                            }
                        }

                    snippets = [
                        {
                            "title": r.get("title", ""),
                            "snippet": r.get("snippet", "")
                        }
                        for r in results[:3]
                    ]

                    # Store in cache
                    self._cache[cache_key] = snippets

                    return {
                        "status": "success",
                        "tool": self.name,
                        "data": {
                            "results": snippets,
                            "cached": False
                        }
                    }

        except httpx.TimeoutException:
            return {
                "status": "error",
                "tool": self.name,
                "error_type": "timeout",
                "message": "Search request timed out."
            }

        except httpx.HTTPError as e:
            return {
                "status": "error",
                "tool": self.name,
                "error_type": "http_failure",
                "message": str(e)
            }

        except Exception as e:
            return {
                "status": "error",
                "tool": self.name,
                "error_type": "unknown_failure",
                "message": str(e)
            }