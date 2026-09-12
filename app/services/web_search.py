"""Internet search adapter with normalized results for research and tutoring."""

import re
from html import unescape
from urllib.parse import quote_plus
from urllib.parse import parse_qs, urlparse

import requests


def search_web(query, limit=8):
    query = (query or "").strip()
    if not query:
        return []
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Edulab/1.0 educational research client"},
            timeout=12,
        )
        response.raise_for_status()
        from html.parser import HTMLParser

        class ResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self.current = None
                self.in_title = False
                self.in_snippet = False

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                classes = attrs.get("class", "")
                if tag == "a" and "result__a" in classes:
                    self.current = {"title": "", "url": attrs.get("href", ""), "snippet": ""}
                    self.in_title = True
                elif self.current and tag in {"a", "div"} and "result__snippet" in classes:
                    self.in_snippet = True

            def handle_data(self, data):
                if self.current and self.in_title:
                    self.current["title"] += data.strip()
                elif self.current and self.in_snippet:
                    self.current["snippet"] += data.strip() + " "

            def handle_endtag(self, tag):
                if tag == "a" and self.in_title:
                    self.in_title = False
                if tag == "div" and self.in_snippet:
                    self.in_snippet = False
                    if self.current.get("title"):
                        item = self.current
                        item["title"] = re.sub(r"\s+", " ", unescape(item["title"])).strip()
                        item["snippet"] = re.sub(r"\s+", " ", unescape(item["snippet"])).strip()
                        parsed = parse_qs(urlparse(item["url"]).query).get("uddg")
                        if parsed:
                            item["url"] = parsed[0]
                        if item["url"].startswith("//"):
                            item["url"] = "https:" + item["url"]
                        self.results.append(item)
                        self.current = None

        parser = ResultParser()
        parser.feed(response.text)
        return parser.results[:limit]
    except (requests.RequestException, ValueError):
        return []


def summarize_results(query, results):
    """Create a short source-grounded summary without inventing facts."""
    usable = [item for item in results if item.get("snippet") or item.get("title")]
    if not usable:
        return "No web sources were available for this query."
    lines = [f"Research summary for: {query}"]
    for index, item in enumerate(usable[:5], 1):
        detail = item.get("snippet") or "No description was provided by the source."
        lines.append(f"{index}. {item.get('title', 'Untitled')}: {detail}")
    lines.append("Open the linked sources to verify details and context.")
    return "\n".join(lines)
