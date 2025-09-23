#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interaktywny konwerter DjVu -> PDF (wersja z obsługą Windows ddjvu.exe)
"""

import os
import sys
import subprocess
import glob
from pathlib import Path
import shutil

def znajdz_ddjvu():
    """
    Zwraca ścieżkę do ddjvu (może być 'ddjvu' lub pełna ścieżka do ddjvu.exe).
    Sprawdza zmienną środowiskową DJVU_PATH, potem shutil.which('ddjvu') i shutil.which('ddjvu.exe').
    Zwraca None jeśli nie znaleziono.
    """
    env_path = os.environ.get('DJVU_PATH')
    if env_path:
        if os.path.isfile(env_path) and os.access(env_path, os.X_OK):
            return env_path
        # jeśli podano katalog zamiast pliku, spróbuj ddjvu w tym katalogu
        if os.path.isdir(env_path):
            candidate = os.path.join(env_path, 'ddjvu.exe' if os.name == 'nt' else 'ddjvu')
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate

    # szukaj w PATH
    for name in ('ddjvu', 'ddjvu.exe'):
        path = shutil.which(name)
        if path:
            return path

    return None

def znajdz_pliki_djvu(katalog):
    wzorce = ['*.djvu', '*.djv', '*.DJVU', '*.DJV']
    pliki = []
    for wzorzec in wzorce:
        pliki.extend(glob.glob(os.path.join(katalog, wzorzec)))
    return sorted(pliki)

def wyswietl_pliki(pliki):
    if not pliki:
        print("❌ Nie znaleziono plików DjVu w podanym katalogu.")
        return
    print(f"\n📁 Znaleziono {len(pliki)} plików DjVu:")
    print("-" * 60)
    for i, plik in enumerate(pliki, 1):
        nazwa = os.path.basename(plik)
        try:
            rozmiar = os.path.getsize(plik) / (1024 * 1024)
            rozmiar_s = f"{rozmiar:.1f} MB"
        except Exception:
            rozmiar_s = "??"
        print(f"{i:2d}. {nazwa} ({rozmiar_s})")

def wybierz_konkretne_pliki(pliki):
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
            print("❌ Nieprawidłowy format. Użyj np. 1,3,5 lub 1-5")

def wybierz_pliki(pliki):
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
            print("❌ Wybierz 1, 2 lub 3")

def konwertuj_plik(ddjvu_path, plik_djvu, katalog_wyjsciowy, jakosc='normal', timeout_s=300):
    nazwa_bez_rozszerzenia = os.path.splitext(os.path.basename(plik_djvu))[0]
    plik_pdf = os.path.join(katalog_wyjsciowy, f"{nazwa_bez_rozszerzenia}.pdf")
    parametry_jakosci = {
        'low': ['-quality=25', '-smooth'],
        'normal': ['-quality=75'],
        'high': ['-quality=100', '-smooth']
    }
    params = parametry_jakosci.get(jakosc, ['-quality=75'])
    cmd = [ddjvu_path, '-format=pdf'] + params + [plik_djvu, plik_pdf]
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
    print("=" * 60)
    print("🔄 KONWERTER DjVu → PDF (Windows-friendly)")
    print("=" * 60)

    ddjvu_path = znajdz_ddjvu()
    if not ddjvu_path:
        print("❌ Nie znaleziono programu ddjvu.")
        print("   - Dodaj ddjvu.exe do PATH lub ustaw zmienną środowiskową DJVU_PATH wskazującą na ddjvu.exe")
        print("   - Strona projektu: http://djvu.sourceforge.net/")
        sys.exit(1)
    else:
        print(f"ℹ️  ddjvu wykryto: {ddjvu_path}")

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

        wybrane_pliki = wybierz_pliki(pliki_djvu)
        if wybrane_pliki is None:
            continue

        katalog_wyjsciowy = input(f"\nKatalog docelowy (Enter = {katalog}): ").strip()
        if not katalog_wyjsciowy:
            katalog_wyjsciowy = katalog
        Path(katalog_wyjsciowy).mkdir(parents=True, exist_ok=True)

        jakosc = wybierz_jakosc()

        # timeout
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

        sukces = 0
        bledy = 0
        for plik in wybrane_pliki:
            if konwertuj_plik(ddjvu_path, plik, katalog_wyjsciowy, jakosc, timeout_s):
                sukces += 1
            else:
                bledy += 1

        print("\n" + "=" * 60)
        print("📊 PODSUMOWANIE")
        print("=" * 60)
        print(f"✅ Pomyślnie skonwertowano: {sukces}")
        print(f"❌ Błędy: {bledy}")
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