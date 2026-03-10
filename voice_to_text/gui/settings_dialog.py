"""Dialog s nastavením aplikace."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
)

from ..settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._settings = settings
        self._build_ui()

    # ------------------------------------------------------------------ #
    # Sestavení UI                                                         #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(20, 20, 20, 20)

        # ── Přepis ──────────────────────────────────────────────────────
        grp_transcription = QGroupBox("Přepis")
        form = QFormLayout(grp_transcription)
        form.setSpacing(10)

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Čeština", "cs")
        self._lang_combo.addItem("English", "en")
        idx = self._lang_combo.findData(self._settings.language)
        self._lang_combo.setCurrentIndex(max(idx, 0))
        form.addRow("Jazyk:", self._lang_combo)

        self._rate_combo = QComboBox()
        self._rate_combo.addItem("16 kHz – rychlejší", 16000)
        self._rate_combo.addItem("44.1 kHz – věrnější", 44100)
        idx = self._rate_combo.findData(self._settings.sample_rate)
        self._rate_combo.setCurrentIndex(max(idx, 0))
        form.addRow("Vzorkovací frekvence:", self._rate_combo)

        root.addWidget(grp_transcription)

        # ── AI zpracování ────────────────────────────────────────────────
        grp_ai = QGroupBox("AI zpracování")
        ai_layout = QVBoxLayout(grp_ai)
        ai_layout.setSpacing(8)

        self._correction_cb = QCheckBox("Opravovat pravopis a čárky")
        self._correction_cb.setChecked(self._settings.use_correction)
        ai_layout.addWidget(self._correction_cb)

        self._translate_cb = QCheckBox("Překládat do angličtiny")
        self._translate_cb.setChecked(self._settings.translate_to_english)
        ai_layout.addWidget(self._translate_cb)

        root.addWidget(grp_ai)

        # ── Tlačítka ─────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    # ------------------------------------------------------------------ #
    # Logika                                                               #
    # ------------------------------------------------------------------ #

    def _on_accept(self) -> None:
        self._settings.language = self._lang_combo.currentData()
        self._settings.sample_rate = self._rate_combo.currentData()
        self._settings.use_correction = self._correction_cb.isChecked()
        self._settings.translate_to_english = self._translate_cb.isChecked()
        self._settings.save()
        self.accept()
