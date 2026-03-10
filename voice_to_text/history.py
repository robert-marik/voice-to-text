"""Perzistentní historie přepisů uložená jako JSON."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import List

from .config import APP_DATA_DIR

HISTORY_PATH = os.path.join(APP_DATA_DIR, "history.json")
MAX_ENTRIES = 200


@dataclass
class TranscriptionEntry:
    timestamp: float
    raw: str
    corrected: str
    language: str
    duration_s: float = 0.0

    @property
    def display_time(self) -> str:
        return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(self.timestamp))

    @property
    def final_text(self) -> str:
        return self.corrected if self.corrected else self.raw


class TranscriptionHistory:
    def __init__(self, path: str = HISTORY_PATH):
        self._path = path
        os.makedirs(APP_DATA_DIR, exist_ok=True)
        self._entries: List[TranscriptionEntry] = self._load()

    # ------------------------------------------------------------------ #

    def add(self, entry: TranscriptionEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > MAX_ENTRIES:
            self._entries = self._entries[:MAX_ENTRIES]
        self._save()

    def all(self) -> List[TranscriptionEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries = []
        self._save()

    # ------------------------------------------------------------------ #

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self._entries], f, ensure_ascii=False, indent=2)

    def _load(self) -> List[TranscriptionEntry]:
        if not os.path.exists(self._path):
            return []
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            return [TranscriptionEntry(**d) for d in data]
        except Exception:
            return []
