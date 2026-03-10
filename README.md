# Voice to Text

Systray applet pro Linux s GUI (PySide6). Nahrává hlas, přepisuje ho přes
Whisper (Groq API) a volitelně opravuje pravopis nebo překládá do angličtiny.

## Požadavky

### Systémové nástroje
```bash
sudo apt install alsa-utils ffmpeg xclip xdotool playerctl
```

### Python závislosti
```bash
pip install -e .
# nebo
pip install groq PySide6 pynput
```

### API klíč
```bash
export GROQ_API_KEY="vas_klic"
```

## Spuštění
```bash
python main.py
```

## Ovládání
- **2× Ctrl** – zahájí / ukončí nahrávání
- **Levý klik na ikonu** – otevře hlavní okno s historií
- **Pravý klik na ikonu** – kontextové menu

## Struktura projektu
```
voice_to_text/
├── main.py                        # Vstupni bod (QApplication)
├── pyproject.toml
├── README.md
└── voice_to_text/
    ├── config.py                  # Konstanty
    ├── settings.py                # Uzivatelska nastaveni (JSON)
    ├── history.py                 # Historie prepisu (JSON)
    ├── logger.py                  # Logovani
    ├── audio.py                   # Nahravani + ffmpeg normalizace
    ├── transcriber.py             # Groq Whisper, korekce, preklad
    ├── clipboard.py               # xclip + xdotool
    ├── music.py                   # playerctl
    ├── tray.py                    # AppController (QSystemTrayIcon)
    └── gui/
        ├── main_window.py         # Hlavni okno s historii prepisu
        └── settings_dialog.py    # Dialog nastaveni
```
