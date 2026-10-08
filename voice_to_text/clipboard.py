"""Vkládání textu do schránky a aktivního okna."""

import subprocess
import time

from .config import use_evdev_input
from .logger import Logger

TERMINALS = ("terminator", "terminal", "xterm", "konsole", "tilix", "kitty", "alacritty", "urxvt", "guake", "wezterm")


class ClipboardPaster:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.wayland = use_evdev_input()
        self._uinput = None
        if self.wayland:
            self._uinput = self._create_uinput()

    def _create_uinput(self):
        """Virtuální klávesnice pro Wayland. Vytváří se hned, aby ji kompozitor stihl zaregistrovat."""
        try:
            from evdev import UInput, ecodes
            return UInput({ecodes.EV_KEY: [ecodes.KEY_LEFTSHIFT, ecodes.KEY_INSERT]},
                          name="voice-to-text-keyboard")
        except Exception as e:
            self.logger.log(f"CHYBA: nelze otevrit /dev/uinput ({e}). Text zustane jen ve schrance. "
                            "Viz README: udev pravidlo 70-voice-to-text-uinput.rules.")
            return None

    @property
    def can_paste(self) -> bool:
        return not self.wayland or self._uinput is not None

    def paste(self, text: str) -> None:
        """Vloží text do schránky (xclip) a pak simuluje klávesy pro vložení."""
        self.logger.log(f"Vkládám: {text}")
        try:
            # ponytail: obnovuje se jen text; obrázek ve schránce se přepíše (řešení: -t TARGETS + -t <mime>)
            # Pod Waylandem vkládáme Shift+Insert, které terminály berou z PRIMARY – plníme proto obě.
            selections = ("clipboard", "primary") if self.wayland else ("clipboard",)
            old = {sel: self._get_clipboard(sel) for sel in selections}
            for sel in selections:
                self._set_clipboard(text.encode("utf-8"), sel)
            if not self.can_paste:
                self.logger.log("Automaticke vlozeni neni dostupne, text je ve schrance (Ctrl+V).")
                return
            time.sleep(0.25)
            self.logger.log("Vkládám text do aktivního okna...")
            if self.wayland:
                self._send_shift_insert()
            else:
                subprocess.run(["xdotool", "key", self._paste_key()], stdin=subprocess.DEVNULL)
            time.sleep(0.5)  # cílová aplikace musí schránku přečíst dřív, než ji vrátíme
            for sel, data in old.items():
                if data is not None:
                    self._set_clipboard(data, sel)
        except Exception as e:
            self.logger.log(f"CHYBA při vkládání: {e}")

    def _send_shift_insert(self) -> None:
        """Shift+Insert vkládá v GTK/Qt aplikacích, prohlížečích i terminálech (na rozdíl od Ctrl+V)."""
        from evdev import ecodes
        ui = self._uinput
        for code, value in ((ecodes.KEY_LEFTSHIFT, 1), (ecodes.KEY_INSERT, 1),
                            (ecodes.KEY_INSERT, 0), (ecodes.KEY_LEFTSHIFT, 0)):
            ui.write(ecodes.EV_KEY, code, value)
            ui.syn()
            time.sleep(0.02)

    @staticmethod
    def _get_clipboard(selection: str) -> bytes | None:
        old = subprocess.run(["xclip", "-selection", selection, "-o"],
                             capture_output=True, stdin=subprocess.DEVNULL, timeout=2)
        return old.stdout if old.returncode == 0 else None

    @staticmethod
    def _set_clipboard(data: bytes, selection: str = "clipboard") -> None:
        process = subprocess.Popen(["xclip", "-selection", selection], stdin=subprocess.PIPE)
        process.communicate(input=data)

    @staticmethod
    def _paste_key() -> str:
        """Terminály vkládají přes Ctrl+Shift+V, ostatní okna přes Ctrl+V."""
        win = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL).stdout.strip()
        wm_class = subprocess.run(["xprop", "-id", win, "WM_CLASS"], capture_output=True, text=True,
                                  stdin=subprocess.DEVNULL).stdout.lower() if win else ""
        return "ctrl+shift+v" if any(t in wm_class for t in TERMINALS) else "ctrl+v"
