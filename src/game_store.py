"""Simple local store for favorite games."""

import json
from pathlib import Path
from typing import List, Dict


class GameStore:
    def __init__(self, path: str = "data/games.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def load(self) -> List[Dict]:
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return []

    def save(self, games: List[Dict]):
        self.path.write_text(json.dumps(games, indent=2))

    def add(self, appid: int, name: str):
        games = self.load()
        if not any(g["appid"] == appid for g in games):
            games.append({"appid": appid, "name": name})
            self.save(games)

    def remove(self, appid: int):
        games = [g for g in self.load() if g["appid"] != appid]
        self.save(games)
