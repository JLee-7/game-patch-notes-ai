"""Steam client for searching games and fetching news/patch notes."""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class SteamClient:
    STORE_SEARCH = "https://store.steampowered.com/api/storesearch/"
    NEWS_API = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GamePatchNotesAI/1.0 (portfolio project)"
        })

    def search_games(self, query: str, country: str = "us") -> List[Dict]:
        """Search Steam store by game name. Returns list of matching apps."""
        params = {
            "term": query,
            "l": "english",
            "cc": country,
        }
        try:
            resp = self.session.get(self.STORE_SEARCH, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            # Filter to actual games/apps
            return [
                {
                    "appid": item["id"],
                    "name": item["name"],
                    "tiny_image": item.get("tiny_image"),
                }
                for item in items
                if item.get("type") == "app"
            ]
        except Exception as e:
            print(f"Steam search error: {e}")
            return []

    def get_news(
        self,
        appid: int,
        count: int = 10,
        maxlength: int = 0,
        tags: Optional[str] = None,
        feeds: Optional[str] = "steam_community_announcements",
    ) -> List[Dict]:
        """Fetch recent publisher news items for a game."""
        params = {
            "appid": appid,
            "count": count,
            "maxlength": maxlength,
        }
        if tags:
            params["tags"] = tags
        if feeds:
            params["feeds"] = feeds

        try:
            resp = self.session.get(self.NEWS_API, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("appnews", {}).get("newsitems", [])
            return [
                {
                    "gid": item.get("gid"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "author": item.get("author"),
                    "contents": item.get("contents", ""),
                    "date": datetime.utcfromtimestamp(item.get("date", 0)).isoformat(),
                    "feedlabel": item.get("feedlabel"),
                    "tags": item.get("tags", []),
                }
                for item in items
            ]
        except Exception as e:
            print(f"Steam news error for {appid}: {e}")
            return []
