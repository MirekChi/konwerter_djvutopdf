========================================
KONWERTER DjVu → PDF - BUDOWANIE EXE
========================================

Ten katalog zawiera pliki do budowania pliku wykonywalnego (.exe) 
z aplikacji konwertera DjVu na PDF.

PLIKI:
- djvu_to_pdf_gui.py          - Główna aplikacja GUI
- DJVU_to_PDF_Converter.spec  - Plik konfiguracyjny PyInstaller
- build_exe.bat               - Skrypt batch do budowania (Windows)
- build_exe.py                - Skrypt Python do budowania (uniwersalny)
- README_BUILD.txt            - Ten plik z instrukcjami

SPOSOBY BUDOWANIA:

1. AUTOMATYCZNY (Zalecany):
   - Uruchom: build_exe.bat (Windows) lub python build_exe.py
   - Skrypt automatycznie zainstaluje PyInstaller jeśli potrzeba
   - Gotowy plik .exe będzie w katalogu dist/

2. RĘCZNY:
   - Zainstaluj PyInstaller: pip install pyinstaller
   - Uruchom: pyinstaller --onefile --windowed --name "DJVU_to_PDF_Converter" djvu_to_pdf_gui.py
   - Plik .exe będzie w katalogu dist/

WYMAGANIA:
- Python 3.6+
- PyInstaller (zostanie zainstalowany automatycznie)
- Narzędzie ddjvu (musi być dostępne w systemie)

WYNIK:
- DJVU_to_PDF_Converter.exe - Gotowy plik wykonywalny
- Rozmiar: ~15-20 MB (zawiera cały interpreter Python)
- Nie wymaga zainstalowanego Pythona na docelowym komputerze

UŻYCIE:
1. Skopiuj plik .exe do dowolnego katalogu
2. Upewnij się, że ddjvu.exe jest w PATH lub ustaw zmienną DJVU_PATH
3. Uruchom plik .exe
4. Użyj interfejsu graficznego do konwersji plików

UWAGI:
- Pierwsze uruchomienie może być wolniejsze (rozpakowywanie)
- Antywirus może ostrzegać o nieznanym pliku (to normalne)
- Aplikacja działa na Windows 7/8/10/11