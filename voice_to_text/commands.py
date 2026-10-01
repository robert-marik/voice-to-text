"""Hlasové příkazy: fuzzy porovnání přepisu s frázemi a spuštění shell příkazu."""

from __future__ import annotations

import difflib
import re
import subprocess

from .config import TERMINAL_CMD


def _norm(s: str) -> str:
    return re.sub(r"[^\w\s]", "", s).casefold().strip()


def match_command(text: str, commands: dict[str, str], cutoff: float = 0.6) -> str | None:
    """Vrátí příkaz, jehož fráze nejlépe odpovídá textu, nebo None."""
    by_norm = {_norm(phrase): cmd for phrase, cmd in commands.items()}
    best = difflib.get_close_matches(_norm(text), list(by_norm), n=1, cutoff=cutoff)
    return by_norm[best[0]] if best else None


def prefill_in_terminal(cmd: str) -> None:
    """Otevře nový terminál s předvyplněným příkazem; spustí se až po Enteru, okno zůstane otevřené."""
    # Příkaz jde jako $0, takže ho není třeba escapovat.
    script = 'read -e -i "$0" -p "$ " c; eval "$c"; exec bash'
    _popen(TERMINAL_CMD + ["bash", "-c", script, cmd])


def run_command(cmd: str) -> None:
    """Spustí příkaz na pozadí; s prefixem "@" v novém terminálu, který po skončení zůstane otevřený.

    S prefixem "!" pošle klávesovou zkratku (syntaxe xdotool, např. "ctrl+grave", více zkratek oddělit mezerou).
    """
    if cmd.startswith("!"):
        cmd = ["xdotool", "key", "--clearmodifiers", *cmd[1:].split()]
    elif cmd.startswith("@"):
        cmd = TERMINAL_CMD + ["bash", "-c", f"{cmd[1:].strip()}; exec bash"]
    _popen(cmd)


def _popen(cmd: str | list[str]) -> None:
    subprocess.Popen(
        cmd, shell=isinstance(cmd, str), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, start_new_session=True,
    )


if __name__ == "__main__":
    cmds = {"otevři kalkulačku": "gnome-calculator", "zamkni obrazovku": "loginctl lock-session"}
    assert match_command("Otevři kalkulačku.", cmds) == "gnome-calculator"
    assert match_command("otevři kalkulacku", cmds) == "gnome-calculator"
    assert match_command("Zamkni obrazovku!", cmds) == "loginctl lock-session"
    assert match_command("dnes je hezky", cmds) is None
    assert match_command("cokoliv", {}) is None
    assert match_command("stav gitu", {"stav gitu": "> git status"}) == "> git status"
    print("ok")
