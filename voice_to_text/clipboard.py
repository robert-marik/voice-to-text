"""Vkládání textu do schránky a aktivního okna."""

import subprocess
import time

from .logger import Logger

TERMINALS = ("terminator", "terminal", "xterm", "konsole", "tilix", "kitty", "alacritty", "urxvt", "guake", "wezterm")


class ClipboardPaster:
    def __init__(self, logger: Logger):
        self.logger = logger

    def paste(self, text: str) -> None:
        """Vloží text do schránky (xclip) a pak simuluje Ctrl+V (xdotool)."""
        self.logger.log(f"Vkládám: {text}")
        try:
            # ponytail: obnovuje se jen text; obrázek ve schránce se přepíše (řešení: -t TARGETS + -t <mime>)
            old = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                                 capture_output=True, stdin=subprocess.DEVNULL, timeout=2)
            self._set_clipboard(text.encode("utf-8"))
            time.sleep(0.25)
            self.logger.log("Vkládám text do aktivního okna...")
            subprocess.run(["xdotool", "key", self._paste_key()], stdin=subprocess.DEVNULL)
            if old.returncode == 0:
                time.sleep(0.5)  # cílová aplikace musí schránku přečíst dřív, než ji vrátíme
                self._set_clipboard(old.stdout)
        except Exception as e:
            self.logger.log(f"CHYBA při vkládání: {e}")

    @staticmethod
    def _set_clipboard(data: bytes) -> None:
        process = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        process.communicate(input=data)

    @staticmethod
    def is_terminal_active() -> bool:
        """Je aktivní okno terminál (podle WM_CLASS)?"""
        win = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL).stdout.strip()
        wm_class = subprocess.run(["xprop", "-id", win, "WM_CLASS"], capture_output=True, text=True,
                                  stdin=subprocess.DEVNULL).stdout.lower() if win else ""
        return any(t in wm_class for t in TERMINALS)

    def _paste_key(self) -> str:
        """Terminály vkládají přes Ctrl+Shift+V, ostatní okna přes Ctrl+V."""
        return "ctrl+shift+v" if self.is_terminal_active() else "ctrl+v"
