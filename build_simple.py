#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uproszczony skrypt do budowania pliku wykonywalnego
"""

import os
import sys
import subprocess
import shutil
import time

def clean_directories():
    """Wyczyść katalogi build"""
    print("🧹 Czyszczenie katalogów...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"   ✅ Usunięto: {directory}")
            except Exception as e:
                print(f"   ⚠️ Nie można usunąć {directory}: {e}")

def install_pyinstaller():
    """Zainstaluj lub zaktualizuj PyInstaller"""
    print("�� Sprawdzanie PyInstaller...")
    
    try:
        import PyInstaller
        print("   ✅ PyInstaller jest zainstalowany")
        return True
    except ImportError:
        print("   ❌ PyInstaller nie jest zainstalowany")
        print("   �� Instaluję PyInstaller...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True, text=True)
            print("   ✅ PyInstaller został zainstalowany")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Błąd instalacji: {e}")
            return False

def build_executable():
    """Zbuduj plik wykonywalny z prostymi opcjami"""
    print("🔨 Budowanie aplikacji...")
    
    # Prosta komenda PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "DJVU_Converter",
        "--clean",
        "djvu_to_pdf_gui.py"
    ]
    
    print(f"   Komenda: {' '.join(cmd)}")
    
    try:
        # Uruchom z timeout
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
        print("   ✅ Budowanie zakończone pomyślnie!")
        return True
        
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout - budowanie trwało zbyt długo")
        return False
    except subprocess.CalledProcessError as e:
        print("   ❌ Błąd podczas budowania:")
        if e.stdout:
            print("   STDOUT:", e.stdout[-500:])  # Ostatnie 500 znaków
        if e.stderr:
            print("   STDERR:", e.stderr[-500:])
        return False

def check_result():
    """Sprawdź czy plik został utworzony"""
    exe_path = "dist/DJVU_Converter.exe"
    
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"   ✅ Plik utworzony: {exe_path}")
        print(f"   📊 Rozmiar: {size:.1f} MB")
        return True
    else:
        print(f"   ❌ Plik nie został utworzony: {exe_path}")
        return False

def main():
    """Główna funkcja"""
    print("=" * 60)
    print("�� BUDOWANIE PLIKU WYKONYWALNEGO")
    print("   Konwerter DjVu → PDF (uproszczone)")
    print("=" * 60)
    print()
    
    # Krok 1: Sprawdź PyInstaller
    if not install_pyinstaller():
        print("\n❌ Nie można kontynuować bez PyInstaller")
        input("Naciśnij Enter aby zakończyć...")
        return
    
    print()
    
    # Krok 2: Wyczyść katalogi
    clean_directories()
    print()
    
    # Krok 3: Zbuduj aplikację
    if build_executable():
        print()
        if check_result():
            print()
            print("=" * 60)
            print("🎉 SUKCES!")
            print("=" * 60)
            print("📁 Plik wykonywalny: dist/DJVU_Converter.exe")
            print("💡 Możesz go skopiować do dowolnego katalogu")
            print()
        else:
            print("\n❌ Budowanie nie powiodło się - sprawdź błędy powyżej")
    else:
        print("\n❌ Błąd podczas budowania")
    
    print()
    input("Naciśnij Enter aby zakończyć...")

if __name__ == "__main__":
    main()