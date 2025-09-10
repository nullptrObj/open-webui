import logging
import os
from pprint import pprint
from typing import Optional
import requests
from open_webui.retrieval.web.main import SearchResult, get_filtered_results
from open_webui.env import SRC_LOG_LEVELS
import argparse
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])
"""
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
"""


def search_bing(
    subscription_key: str,
    endpoint: str,
    locale: str,
    query: str,
    count: int,
    filter_list: Optional[list[str]] = None,
) -> list[SearchResult]:
    try:
        if endpoint == "https://cn.bing.com/search" or endpoint == "https://bing.com/search":
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/127.0.0.0 Safari/537.36",
            }
            response = requests.get(f"{endpoint}?q={query}", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            contexts = []
            for b in soup.find_all(class_='b_algo')[:count]:
                title = b.find("h2").find("a").text if b.find("h2") else ""
                href = b.find('a')['href']
                if href.startswith('http'):
                    snippet = b.find('p').text if b.find('p') else ""
                    if snippet != "":
                        contexts.append(
                            {'id': href, 'url': href, 'name': title, 'snippet': snippet}
                        )
        else:
            mkt = locale
            params = {"q": query, "mkt": mkt, "count": count}
            headers = {"Ocp-Apim-Subscription-Key": subscription_key}

            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            json_response = response.json()
            results = json_response.get("webPages", {}).get("value", [])
            if filter_list:
                results = get_filtered_results(results, filter_list)
            contexts = [
                {
                    "url": r["url"],
                    "name": r.get("name"),
                    "snippet": r.get("snippet", ""),
                }
                for r in results
            ]

        return [
            SearchResult(link=c["url"], title=c.get("name"), snippet=c.get("snippet"))
            for c in contexts[:count]
        ]
    except Exception as ex:
        log.error(f"Error: {ex}")
        raise ex


def main():
    parser = argparse.ArgumentParser(description="Search Bing from the command line.")
    parser.add_argument(
        "query",
        type=str,
        default="Top 10 international news today",
        help="The search query.",
    )
    parser.add_argument(
        "--count", type=int, default=10, help="Number of search results to return."
    )
    parser.add_argument(
        "--filter", nargs="*", help="List of filters to apply to the search results."
    )
    parser.add_argument(
        "--locale",
        type=str,
        default="en-US",
        help="The locale to use for the search, maps to market in api",
    )

    args = parser.parse_args()

    results = search_bing(args.locale, args.query, args.count, args.filter)
    pprint(results)
