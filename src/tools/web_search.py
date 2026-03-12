import re
import httpx
from ddgs import DDGS
from agents import function_tool, RunContextWrapper


@function_tool
def web_search(ctx: RunContextWrapper, query: str, max_results: int = 3) -> str:
    """Search the web for up-to-date information and return extracted page content.

    Searches DuckDuckGo for the query, fetches the top pages, and returns
    their extracted text concatenated together. Use this for any question
    that requires current information, definitions, or explanations you
    don't have in your training data.

    Args:
        query: The search query.
        max_results: Number of pages to fetch and extract (default 3).
    """
    results = DDGS().text(query, max_results=max_results)
    if not results:
        return "No results found for this query."

    sections: list[str] = []

    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("href", "")
        snippet = r.get("body", "")

        # Try to fetch and extract richer page content
        page_text = _fetch_text(url)
        content = page_text if page_text else snippet

        sections.append(
            f"[Result {i}] {title}\n"
            f"Source: {url}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(sections)


def _fetch_text(url: str) -> str:
    """Fetch a URL and return the first 1000 characters of plain text."""
    if not url:
        return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (research bot)"}
        response = httpx.get(url, headers=headers, timeout=8, follow_redirects=True)
        response.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", response.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:1000]
    except Exception:
        return ""
