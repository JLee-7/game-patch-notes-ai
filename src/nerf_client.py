"""Nerf Radar client for structured patch notes on supported competitive games."""

import requests
from typing import List, Dict, Optional


class NerfRadarClient:
    BASE = "https://nerfradar.com/api"

    def __init__(self):
        self.session = requests.Session()

    def get_games(self) -> List[Dict]:
        """Free endpoint: list of tracked games."""
        try:
            resp = self.session.get(f"{self.BASE}/games", timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Nerf Radar games error: {e}")
            return []

    def get_patches(self, game_slug: str, limit: int = 5) -> List[Dict]:
        """Free endpoint: latest patches with TL;DR for a game."""
        try:
            params = {"game": game_slug, "limit": limit}
            resp = self.session.get(f"{self.BASE}/patches", params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Nerf Radar patches error: {e}")
            return []
