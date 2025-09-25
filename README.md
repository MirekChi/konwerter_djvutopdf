# Konwerter DjVu do PDF

Wszechstronne narzędzie do konwersji plików DjVu do formatu PDF, dostępne zarówno w interfejsie wiersza poleceń (CLI), jak i w graficznym interfejsie użytkownika (GUI).

## Opis ogólny

Ten projekt dostarcza dwa proste, ale potężne skrypty w Pythonie do obsługi konwersji plików DjVu do szerzej obsługiwanego formatu PDF. Konwersja jest realizowana przy użyciu narzędzia wiersza poleceń `ddjvu` z biblioteki DjVuLibre.

- **`djvu_to_pdf.py`**: Interaktywna aplikacja konsolowa dla użytkowników preferujących wiersz poleceń.
- **`djvu_to_pdf_gui.py`**: Przyjazna dla użytkownika aplikacja desktopowa zbudowana w oparciu o Tkinter do wizualnej interakcji.

## Funkcje

- **Podwójny interfejs**: Wybierz między narzędziem konsolowym a w pełni funkcjonalnym GUI.
- **Elastyczny wybór plików**: Konwertuj pojedyncze pliki, wiele plików lub całe katalogi naraz.
- **Kontrola jakości**: Wybieraj między niską, normalną a wysoką jakością konwersji, aby zrównoważyć rozmiar pliku i rozdzielczość.
- **Niestandardowe wyjście**: Zapisuj przekonwertowane pliki w określonym katalogu lub w tym samym katalogu co pliki źródłowe.
- **Wieloplatformowość**: Napisany w Pythonie, dzięki czemu jest kompatybilny z systemami Windows, macOS i Linux (wymaga zainstalowanego `ddjvu`).
- **Samodzielny plik wykonywalny**: Dostępne są skrypty do spakowania aplikacji GUI w jeden plik `.exe` dla systemu Windows, który nie wymaga instalacji Pythona.

## Wymagania

### 1. Python

- Wymagany jest Python 3.6 lub nowszy.

### 2. ddjvu

To narzędzie jest nakładką na narzędzie wiersza poleceń `ddjvu`, które musi być zainstalowane w systemie.

- **Instalacja**: `ddjvu` jest częścią biblioteki **DjVuLibre**. Instalatory i kod źródłowy można znaleźć na oficjalnej stronie projektu: [http://djvu.sourceforge.net/](http://djvu.sourceforge.net/)
- **Konfiguracja**: Po instalacji upewnij się, że plik wykonywalny `ddjvu` (`ddjvu.exe` w systemie Windows) jest dostępny dla skryptu. Masz dwie opcje:
    1.  **Dodaj do PATH**: Dodaj katalog zawierający `ddjvu` do zmiennej środowiskowej `PATH` systemu. Jest to zalecane podejście.
    2.  **Ustaw DJVU_PATH**: Alternatywnie, utwórz zmienną środowiskową o nazwie `DJVU_PATH` i ustaw jej wartość na pełną ścieżkę do pliku wykonywalnego `ddjvu`.

Aplikacja automatycznie wykryje plik wykonywalny `ddjvu`, jeśli jest on poprawnie skonfigurowany.

## Użycie

### Wersja konsolowa

Aplikacja konsolowa zapewnia interaktywny, krok po kroku proces konwersji plików.

1.  **Przejdź** do katalogu projektu w terminalu.
2.  **Uruchom skrypt**:
    ```bash
    python djvu_to_pdf.py
    ```
3.  **Postępuj zgodnie z instrukcjami**:
    - Wprowadź ścieżkę do katalogu zawierającego pliki DjVu.
    - Wybierz, czy chcesz konwertować wszystkie pliki, czy wybrać konkretne.
    - Wybierz jakość konwersji.
    - Określ katalog wyjściowy.
    - Potwierdź, aby rozpocząć konwersję.

### Wersja GUI

GUI zapewnia bardziej wizualny sposób zarządzania procesem konwersji.

1.  **Przejdź** do katalogu projektu.
2.  **Uruchom skrypt**:
    ```bash
    python djvu_to_pdf_gui.py
    ```
3.  **Korzystaj z interfejsu**:
    - Użyj przycisków "Wybierz pliki DjVu" lub "Wybierz katalog", aby dodać pliki do listy konwersji.
    - Dostosuj ustawienia jakości, limitu czasu i katalogu wyjściowego.
    - Kliknij "Rozpocznij konwersję", aby rozpocząć. Postęp będzie widoczny w oknie logu.

## Budowanie pliku wykonywalnego (Windows)

Możesz utworzyć samodzielny plik `.exe` dla aplikacji GUI, który działa w systemie Windows bez konieczności instalowania Pythona.

- **Automatyczne (zalecane)**: Uruchom skrypt `build_console.bat`. Automatycznie zainstaluje on zależności (takie jak PyInstaller) i wygeneruje plik wykonywalny w folderze `dist/`.
- **Ręczne**:
    1.  Zainstaluj PyInstaller: `pip install pyinstaller`
    2.  Uruchom polecenie:
        ```bash
        pyinstaller --onefile --windowed --name "DJVU_to_PDF_Converter" djvu_to_pdf_gui.py
        ```
Finalny plik `DJVU_to_PDF_Converter.exe` będzie znajdował się w katalogu `dist/`.

## Licencja

Ten projekt jest oprogramowaniem typu open-source i jest dostępny na [Licencji MIT](LICENSE).