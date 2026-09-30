"""Vkládání textu do schránky a aktivního okna."""

import subprocess
import time

from .logger import Logger


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
            subprocess.run(["xdotool", "key", "ctrl+v"], stdin=subprocess.DEVNULL)
            if old.returncode == 0:
                time.sleep(0.5)  # cílová aplikace musí schránku přečíst dřív, než ji vrátíme
                self._set_clipboard(old.stdout)
        except Exception as e:
            self.logger.log(f"CHYBA při vkládání: {e}")

    @staticmethod
    def _set_clipboard(data: bytes) -> None:
        process = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        process.communicate(input=data)
