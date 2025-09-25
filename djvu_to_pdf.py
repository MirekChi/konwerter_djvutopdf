#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interaktywny konwerter DjVu -> PDF (wersja konsolowa).

Ten skrypt pozwala użytkownikom na konwersję plików DjVu do formatu PDF
przy użyciu narzędzia wiersza poleceń `ddjvu`. Jest zaprojektowany z myślą
o łatwości obsługi i dobrze działa w systemie Windows, gdzie `ddjvu.exe` jest popularne.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path
import shutil

def znajdz_ddjvu():
    """Znajduje ścieżkę do pliku wykonywalnego ddjvu.

    Sprawdza najpierw zmienną środowiskową DJVU_PATH. Jeśli nie zostanie znaleziona,
    przeszukuje systemową zmienną PATH w poszukiwaniu 'ddjvu' lub 'ddjvu.exe'.

    Zwraca:
        str: Pełna ścieżka do pliku wykonywalnego ddjvu lub None, jeśli nie znaleziono.
    """
    env_path = os.environ.get('DJVU_PATH')
    if env_path:
        if os.path.isfile(env_path) and os.access(env_path, os.X_OK):
            return env_path
        # Jeśli podano katalog, spróbuj znaleźć w nim ddjvu
        if os.path.isdir(env_path):
            candidate = os.path.join(env_path, 'ddjvu.exe' if os.name == 'nt' else 'ddjvu')
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate

    # Szukaj w PATH
    for name in ('ddjvu', 'ddjvu.exe'):
        path = shutil.which(name)
        if path:
            return path

    return None

def znajdz_pliki_djvu(katalog):
    """Znajduje wszystkie pliki DjVu w podanym katalogu.

    Args:
        katalog (str): Ścieżka do katalogu do przeszukania.

    Zwraca:
        list[str]: Posortowana lista ścieżek do znalezionych plików DjVu.
    """
    wzorce = ['*.djvu', '*.djv', '*.DJVU', '*.DJV']
    pliki = []
    for wzorzec in wzorce:
        pliki.extend(glob.glob(os.path.join(katalog, wzorzec)))
    return sorted(pliki)

def wyswietl_pliki(pliki):
    """Wyświetla numerowaną listę plików wraz z ich rozmiarami.

    Args:
        pliki (list[str]): Lista ścieżek plików do wyświetlenia.
    """
    if not pliki:
        print("❌ Nie znaleziono plików DjVu w podanym katalogu.")
        return
    print(f"\n📁 Znaleziono {len(pliki)} plików DjVu:")
    print("-" * 60)
    for i, sciezka_pliku in enumerate(pliki, 1):
        nazwa_pliku = os.path.basename(sciezka_pliku)
        try:
            rozmiar_mb = os.path.getsize(sciezka_pliku) / (1024 * 1024)
            rozmiar_str = f"{rozmiar_mb:.1f} MB"
        except Exception:
            rozmiar_str = "??"
        print(f"{i:2d}. {nazwa_pliku} ({rozmiar_str})")

def wybierz_konkretne_pliki(pliki):
    """Prosi użytkownika o wybranie konkretnych plików z listy po numerach.

    Użytkownik może podać numery oddzielone przecinkami lub zakresy (np. "1,3,5-7").

    Args:
        pliki (list[str]): Lista plików do wyboru.

    Zwraca:
        list[str]: Lista ścieżek plików wybranych przez użytkownika.
    """
    while True:
        wybor = input("\nPodaj numery plików (np. 1,3,5 lub 1-5): ").strip()
        try:
            wybrane_indeksy = set()
            for czesc in wybor.split(','):
                czesc = czesc.strip()
                if not czesc:
                    continue
                if '-' in czesc:
                    start, koniec = map(int, czesc.split('-'))
                    wybrane_indeksy.update(range(start, koniec + 1))
                else:
                    wybrane_indeksy.add(int(czesc))
            if not wybrane_indeksy:
                print("❌ Nic nie wybrano.")
                continue
            if all(1 <= i <= len(pliki) for i in wybrane_indeksy):
                return [pliki[i-1] for i in sorted(wybrane_indeksy)]
            else:
                print(f"❌ Numery muszą być z zakresu 1-{len(pliki)}")
        except ValueError:
            print("❌ Nieprawidłowy format. Użyj numerów i zakresów (np. 1,3,5 lub 1-5).")

def wybierz_pliki_do_konwersji(pliki):
    """Umożliwia użytkownikowi wybór plików do konwersji.

    Args:
        pliki (list[str]): Lista dostępnych plików.

    Zwraca:
        list[str] | None: Lista wybranych ścieżek plików lub None, aby wrócić.
    """
    while True:
        print("\n🔧 Opcje wyboru:")
        print("1. Wszystkie pliki")
        print("2. Wybierz konkretne pliki (np. 1,3,5 lub 1-5)")
        print("3. Powrót do wyboru katalogu")
        wybor = input("\nTwój wybór: ").strip()
        if wybor == '1':
            return pliki
        elif wybor == '2':
            return wybierz_konkretne_pliki(pliki)
        elif wybor == '3':
            return None
        else:
            print("❌ Nieprawidłowy wybór. Spróbuj ponownie.")

def wybierz_jakosc():
    """Prosi użytkownika o wybór jakości konwersji.

    Zwraca:
        str: Wybrany poziom jakości ('low', 'normal' lub 'high').
    """
    print("\n🎨 Wybierz jakość konwersji:")
    print("1. Niska (szybka, mały rozmiar)")
    print("2. Normalna (zalecana)")
    print("3. Wysoka (wolna, duży rozmiar)")
    while True:
        wybor = input("\nTwój wybór (1-3): ").strip()
        if wybor == '1':
            return 'low'
        elif wybor == '2':
            return 'normal'
        elif wybor == '3':
            return 'high'
        else:
            print("❌ Wybierz 1, 2 lub 3.")

def konwertuj_plik(sciezka_ddjvu, plik_djvu, katalog_wyjsciowy, jakosc='normal', timeout_s=300):
    """Konwertuje pojedynczy plik DjVu do formatu PDF za pomocą narzędzia ddjvu.

    Args:
        sciezka_ddjvu (str): Ścieżka do pliku wykonywalnego ddjvu.
        plik_djvu (str): Ścieżka do źródłowego pliku DjVu.
        katalog_wyjsciowy (str): Katalog, w którym ma być zapisany przekonwertowany plik PDF.
        jakosc (str, optional): Jakość konwersji.
            Może być 'low', 'normal' lub 'high'. Domyślnie 'normal'.
        timeout_s (int, optional): Timeout konwersji w sekundach.
            Domyślnie 300.

    Zwraca:
        bool: True, jeśli konwersja się powiodła, w przeciwnym razie False.
    """
    nazwa_bazowa = os.path.splitext(os.path.basename(plik_djvu))[0]
    plik_pdf = os.path.join(katalog_wyjsciowy, f"{nazwa_bazowa}.pdf")
    parametry_jakosci = {
        'low': ['-quality=25', '-smooth'],
        'normal': ['-quality=75'],
        'high': ['-quality=100', '-smooth']
    }
    params = parametry_jakosci.get(jakosc, ['-quality=75'])
    cmd = [sciezka_ddjvu, '-format=pdf'] + params + [plik_djvu, plik_pdf]
    print(f"🔄 Konwertuję: {os.path.basename(plik_djvu)} -> {os.path.basename(plik_pdf)}")
    try:
        wynik = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        if wynik.returncode == 0:
            try:
                rozmiar_mb = os.path.getsize(plik_pdf) / (1024 * 1024)
                print(f"✅ Utworzono: {os.path.basename(plik_pdf)} ({rozmiar_mb:.1f} MB)")
            except Exception:
                print(f"✅ Utworzono: {os.path.basename(plik_pdf)}")
            return True
        else:
            print(f"❌ Błąd konwersji (kod {wynik.returncode}). stdout/stderr:")
            if wynik.stdout:
                print("---- STDOUT ----")
                print(wynik.stdout)
            if wynik.stderr:
                print("---- STDERR ----")
                print(wynik.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Przekroczono limit czasu ({timeout_s}s) dla pliku: {os.path.basename(plik_djvu)}")
        return False
    except FileNotFoundError:
        print("❌ Nie znaleziono ddjvu — sprawdź czy ddjvu.exe jest w PATH lub DJVU_PATH.")
        return False
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        return False

def main():
    """Główna funkcja uruchamiająca interaktywny konwerter DjVu na PDF."""
    print("=" * 60)
    print("🔄 KONWERTER DjVu → PDF (Windows-friendly)")
    print("=" * 60)

    sciezka_ddjvu = znajdz_ddjvu()
    if not sciezka_ddjvu:
        print("❌ Nie znaleziono programu ddjvu.")
        print("   - Dodaj ddjvu.exe do systemowej zmiennej PATH lub ustaw zmienną środowiskową DJVU_PATH.")
        print("   - Strona projektu: http://djvu.sourceforge.net/")
        sys.exit(1)
    else:
        print(f"ℹ️  Wykryto ddjvu: {sciezka_ddjvu}")

    while True:
        print(f"\n📂 Aktualny katalog: {os.getcwd()}")
        katalog = input("Podaj ścieżkę do katalogu z plikami DjVu (Enter = aktualny): ").strip()
        if not katalog:
            katalog = os.getcwd()
        if not os.path.isdir(katalog):
            print("❌ Podany katalog nie istnieje!")
            continue

        pliki_djvu = znajdz_pliki_djvu(katalog)
        wyswietl_pliki(pliki_djvu)
        if not pliki_djvu:
            if input("\nSpróbować inny katalog? (t/n): ").lower().startswith('t'):
                continue
            else:
                break

        wybrane_pliki = wybierz_pliki_do_konwersji(pliki_djvu)
        if wybrane_pliki is None:
            continue

        katalog_wyjsciowy = input(f"\nKatalog docelowy (Enter = {katalog}): ").strip()
        if not katalog_wyjsciowy:
            katalog_wyjsciowy = katalog
        Path(katalog_wyjsciowy).mkdir(parents=True, exist_ok=True)

        jakosc = wybierz_jakosc()

        try:
            timeout_s = int(input("\nTimeout konwersji w sekundach (Enter = 300): ").strip() or "300")
        except ValueError:
            timeout_s = 300

        print(f"\n📋 Podsumowanie:")
        print(f"   Plików do konwersji: {len(wybrane_pliki)}")
        print(f"   Katalog docelowy: {katalog_wyjsciowy}")
        print(f"   Jakość: {jakosc}")
        print(f"   Timeout: {timeout_s}s")

        if not input("\nRozpocząć konwersję? (t/n): ").lower().startswith('t'):
            continue

        licznik_sukcesow = 0
        licznik_bledow = 0
        for sciezka_pliku in wybrane_pliki:
            if konwertuj_plik(sciezka_ddjvu, sciezka_pliku, katalog_wyjsciowy, jakosc, timeout_s):
                licznik_sukcesow += 1
            else:
                licznik_bledow += 1

        print("\n" + "=" * 60)
        print("📊 PODSUMOWANIE")
        print("=" * 60)
        print(f"✅ Pomyślnie skonwertowano: {licznik_sukcesow}")
        print(f"❌ Błędy: {licznik_bledow}")
        print(f"📁 Pliki PDF zapisano w: {katalog_wyjsciowy}")

        if not input("\nKonwertować kolejne pliki? (t/n): ").lower().startswith('t'):
            break

    print("\n👋 Dziękuję za skorzystanie z konwertera!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Program przerwany przez użytkownika.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Nieoczekiwany błąd: {e}")
        sys.exit(1)