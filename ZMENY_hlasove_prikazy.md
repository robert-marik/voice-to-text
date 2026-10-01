# Hlasové příkazy – popis změn (necommitováno, čeká na vyzkoušení)

## Chování
- **2× Ctrl krátce** – původní diktování (start, další 2× Ctrl = stop, oprava, vložení).
- **2× Ctrl, druhý stisk podržet** (≥ `HOLD_SECONDS` = 0,5 s) – nahrává se jen během držení.
  Po puštění se přepis (bez korekce a překladu) fuzzy porovná s frázemi
  (`difflib.get_close_matches`, cutoff 0,6, ignoruje velikost písmen a interpunkci)
  a provede se příkaz nejpodobnější fráze. Bez shody jen notifikace „Příkaz nerozpoznán“.
- Nahrávání startuje hned při druhém stisku; o režimu se rozhoduje až při puštění Ctrl.

## Definice příkazů
Nastavení → záložka „🗣 Příkazy“, jeden řádek = `fráze = příkaz`, řádky s `#` se ignorují.
Ukládá se do `~/.local/state/voice_to_text/settings.json` jako `voice_commands`.

| Zápis | Akce |
|---|---|
| `fráze = příkaz` | spustí příkaz na pozadí (`shell=True`) |
| `fráze = > příkaz` | vypíše příkaz do aktivního terminálu a čeká na Enter; není-li aktivní terminál, otevře nový terminator s předvyplněným příkazem (`read -e -i`), okno po skončení zůstane otevřené |
| `fráze = @ příkaz` | spustí v novém terminatoru (`bash -c "příkaz; exec bash"`), okno zůstane otevřené |
| `fráze = ! ctrl+grave` | stiskne klávesovou zkratku přes `xdotool key --clearmodifiers` (názvy kláves podle xdotool, více zkratek oddělit mezerou) |

## Změněné soubory
- `voice_to_text/commands.py` (nový) – `match_command`, `run_command` (prefixy `@`, `!`),
  `prefill_in_terminal`; self-check `python -m voice_to_text.commands`.
- `voice_to_text/tray.py` – `on_release` listener, rozlišení tap/hold, `_run_voice_command`
  (prefix `>` + detekce terminálu), větev příkazového režimu v `_record_and_process`.
- `voice_to_text/clipboard.py` – `is_terminal_active()` vyčleněno z `_paste_key()`.
- `voice_to_text/config.py` – `HOLD_SECONDS`, `TERMINAL_CMD = ["terminator", "-x"]`.
- `voice_to_text/settings.py` – pole `voice_commands`.
- `voice_to_text/gui/settings_dialog.py` – záložka Příkazy (textové pole + parsování).
- `voice_to_text/gui/main_window.py` – text stavu „idle“.
- `README.md`, `README_en.md` – popis hlasových příkazů.

## Ověřeno
- Self-check porovnávání, import aplikace, parsování řádků v dialogu (offscreen).
- Předvyplnění `read -e -i` zachová uvozovky i roury.

## K vyzkoušení ručně
1. 2× Ctrl krátce → diktování funguje jako dřív.
2. Podržený 2. stisk + fráze na pozadí (např. `gnome-calculator`).
3. `>` v aktivním terminálu → vloží se, čeká na Enter.
4. `>` v jiném okně → otevře se terminator s předvyplněným příkazem.
5. `@` → terminator spustí příkaz a zůstane otevřený.
6. `!` → zkratka (např. `ctrl+grave`) se provede v cílové aplikaci.
7. Nesmyslná fráze → notifikace „Příkaz nerozpoznán“, nic se nevloží.

## Známá omezení
- Ctrl+C v předvyplněném řádku (`>` v novém terminálu) okno zavře.
- Terminál je napevno terminator (`TERMINAL_CMD` v `config.py`).
- Příkazy se editují v textovém poli, ne v tabulce.
