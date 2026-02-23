import json
import os
from typing import Any, Dict, List, Optional

import requests
from langchain.tools import tool


class NewsTool:
    """
    Simple wrapper for a news API.

    By default this uses the NewsAPI.org `top-headlines` endpoint.
    Configure the API key and optional base URL via environment variables:

    - NEWS_API_KEY: required, your NewsAPI key
    - NEWS_API_BASE_URL: optional, defaults to "https://newsapi.org/v2/top-headlines"
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError(f"{os.getenv('NEWS_API_KEY')} is not set.")
        self.base_url = os.getenv("NEWS_API_BASE_URL", "https://newsapi.org/v2/top-headlines")

    def get_top_headlines(
        self,
        country: str = "us",
    ) -> List[Dict[str, Any]]:
        """Fetch top headlines and return a simplified list of articles."""
        params: Dict[str, Any] = {
            "apiKey": self.api_key,
        }

        # NewsAPI 需要至少一個 filter（country / category / sources / q）
        if country:
            params["country"] = country
        else:
            # 如果沒有指定國家，就給一個簡單關鍵字，避免 400 Bad Request
            params["q"] = "news"

        response = requests.get(self.base_url, params=params, timeout=10)
        print(response.url)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        simplified: List[Dict[str, Any]] = []
        for article in articles:
            simplified.append(
                {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "source": (article.get("source") or {}).get("name"),
                    "publishedAt": article.get("publishedAt"),
                }
            )
        return simplified


@tool
def get_latest_news(
    country: str = "",
) -> str:
    """
    取得最新新聞列表，並以 JSON 字串形式回傳。
    """
    tool_impl = NewsTool()
    articles = tool_impl.get_top_headlines(country=country)
    # 使用 JSON，方便後續由 LLM 做摘要與重組
    return json.dumps(articles, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Quick manual test
    try:
        tool_impl = NewsTool()
        print(json.dumps(tool_impl.get_top_headlines(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"Error fetching news: {exc}")
