@echo off
echo ========================================
echo  Budowanie pliku wykonywalnego (uproszczone)
echo  Konwerter DjVu -> PDF
echo ========================================
echo.

REM Sprawdź czy PyInstaller jest zainstalowany
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller nie jest zainstalowany!
    echo Instaluję PyInstaller...
    pip install pyinstaller
)

echo.
echo Czyszczenie poprzednich buildów...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo Budowanie aplikacji (prosta komenda)...
pyinstaller --onefile --windowed --name "DJVU_Converter" djvu_to_pdf_gui.py

echo.
echo ========================================
echo  Sprawdzanie rezultatu...
echo ========================================
if exist "dist\DJVU_Converter.exe" (
    echo ✅ SUKCES! Plik wykonywalny utworzony.
    echo �� Lokalizacja: dist\DJVU_Converter.exe
) else (
    echo ❌ Błąd - plik nie został utworzony.
)

echo.
echo Naciśnij dowolny klawisz aby zakończyć...
pause >nul