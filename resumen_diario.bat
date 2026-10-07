@echo off
chcp 65001 >nul

cd /d "%~dp0"

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set FECHA=%%I

echo ============================================================ >> "resumen_diario.log"
echo [%date% %time%] Iniciando resumen diario... >> "resumen_diario.log"

where python >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: no se encontro "python" en el PATH. Instala Python y marca "Add python.exe to PATH". >> "resumen_diario.log"
    exit /b 4
)

if exist "resumen.md" (
    del /q "resumen.md"
)
if exist "resumen.html" (
    del /q "resumen.html"
)

python "%~dp0conectar_correo.py" --resumen 100 --credenciales "%~dp0credenciales.txt" >> "resumen_diario.log" 2>&1

if not exist "resumen.html" (
    echo [%date% %time%] ERROR: no se genero resumen.html >> "resumen_diario.log"
    exit /b 2
)

copy /Y "resumen.html" "%USERPROFILE%\Desktop\resumen_diario_%FECHA%.html" >nul

if errorlevel 1 (
    echo [%date% %time%] ERROR: no se pudo copiar el resumen al Escritorio. >> "resumen_diario.log"
    exit /b 3
)

echo [%date% %time%] OK: resumen generado correctamente. >> "resumen_diario.log"
echo [%date% %time%] OK: copiado como resumen_diario_%FECHA%.html >> "resumen_diario.log"
echo [%date% %time%] Fin del resumen diario. >> "resumen_diario.log"

exit /b 0
