"""Uživatelská nastavení perzistovaná jako JSON."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from .config import (
    APP_DATA_DIR, DEFAULT_LANGUAGE, DEFAULT_SAMPLE_RATE,
    REMOVE_SOUND_FILES, MAX_RECORDING_SECONDS, DEFAULT_TARGET_LANGUAGE,
)

SETTINGS_PATH = os.path.join(APP_DATA_DIR, "settings.json")
_KEYRING_SERVICE, _KEYRING_USER = "voice_to_text", "groq_api_key"


def get_api_key() -> str:
    """API klíč ze systémové klíčenky; prázdný řetězec, pokud chybí nebo klíčenka není dostupná."""
    try:
        return keyring.get_password(_KEYRING_SERVICE, _KEYRING_USER) or ""
    except KeyringError:
        return ""


def set_api_key(key: str) -> None:
    """Uloží klíč do klíčenky, prázdný klíč smaže. Při nedostupné klíčence vyhodí KeyringError."""
    if key:
        keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER, key)
    else:
        try:
            keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USER)
        except PasswordDeleteError:
            pass


@dataclass
class Settings:
    language: str = DEFAULT_LANGUAGE
    sample_rate: int = DEFAULT_SAMPLE_RATE
    use_correction: bool = True
    translate_to_english: bool = False
    target_language: str = DEFAULT_TARGET_LANGUAGE
    remove_sound_files: bool = REMOVE_SOUND_FILES
    max_recording_seconds: int = MAX_RECORDING_SECONDS
    # Vlastní prompty pro korekci, klíč = kód jazyka nahrávky (např. "cs", "en").
    # Prázdný řetězec = použij defaultní prompt.
    custom_correction_prompts: Dict[str, str] = field(default_factory=dict)
    # Vlastní prompty pro překlad, klíč = kód cílového jazyka (např. "en", "de").
    custom_translation_prompts: Dict[str, str] = field(default_factory=dict)
    # Hlasové příkazy: fráze → shell příkaz (2× Ctrl + držet).
    voice_commands: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------ #

    def save(self, path: str = SETTINGS_PATH) -> None:
        os.makedirs(APP_DATA_DIR, exist_ok=True)
        # 0o600: soubor obsahuje i shell příkazy
        with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
        os.chmod(path, 0o600)   # i pro soubor, který už existoval s jinými právy

    @classmethod
    def load(cls, path: str = SETTINGS_PATH) -> "Settings":
        if not os.path.exists(path):
            return cls()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            settings = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()
        if old_key := data.get("groq_api_key"):
            # migrace ze starých verzí: klíč přesunout z JSON do klíčenky
            try:
                set_api_key(old_key)
                settings.save(path)
            except KeyringError:
                os.environ.setdefault("GROQ_API_KEY", old_key)   # soubor nechat, klíč neztratit
        return settings

    def effective_api_key(self) -> str:
        """Vrátí API klíč – z klíčenky nebo z env proměnné."""
        return get_api_key() or os.environ.get("GROQ_API_KEY", "")

    def get_correction_prompt(self, language: str) -> str:
        """Vrátí vlastní prompt pro korekci daného jazyka, nebo prázdný řetězec."""
        return self.custom_correction_prompts.get(language, "")

    def set_correction_prompt(self, language: str, prompt: str) -> None:
        if prompt.strip():
            self.custom_correction_prompts[language] = prompt.strip()
        else:
            self.custom_correction_prompts.pop(language, None)

    def get_translation_prompt(self, target_language: str) -> str:
        """Vrátí vlastní prompt pro překlad do daného jazyka, nebo prázdný řetězec."""
        return self.custom_translation_prompts.get(target_language, "")

    def set_translation_prompt(self, target_language: str, prompt: str) -> None:
        if prompt.strip():
            self.custom_translation_prompts[target_language] = prompt.strip()
        else:
            self.custom_translation_prompts.pop(target_language, None)


if __name__ == "__main__":
    import tempfile
    from keyring.backend import KeyringBackend

    class _MemoryKeyring(KeyringBackend):
        priority = 1
        store: dict = {}
        def get_password(self, service, user): return self.store.get((service, user))
        def set_password(self, service, user, pw): self.store[(service, user)] = pw
        def delete_password(self, service, user):
            if self.store.pop((service, user), None) is None:
                raise PasswordDeleteError(user)

    keyring.set_keyring(_MemoryKeyring())
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "settings.json")
        with open(path, "w") as f:
            json.dump({"language": "en", "groq_api_key": "gsk_test"}, f)
        s = Settings.load(path)
        assert s.language == "en" and get_api_key() == "gsk_test"
        assert "groq_api_key" not in open(path).read()
        assert os.stat(path).st_mode & 0o777 == 0o600
        set_api_key("")
        set_api_key("")   # smazání neexistujícího klíče nesmí spadnout
        assert get_api_key() == ""
    print("ok")
