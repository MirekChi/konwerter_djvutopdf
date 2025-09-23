@echo off
echo ========================================
echo  Budowanie z konsolą (debug)
echo ========================================

pyinstaller --onefile --name "DJVU_Converter_Console" djvu_to_pdf_gui.py

echo.
if exist "dist\DJVU_Converter_Console.exe" (
    echo ✅ Plik utworzony: dist\DJVU_Converter_Console.exe
    echo �� Uruchom go aby zobaczyć ewentualne błędy
) else (
    echo ❌ Błąd budowania
)

pause