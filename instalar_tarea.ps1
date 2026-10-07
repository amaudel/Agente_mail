# Instala la tarea programada "ResumenCorreoDiario" (diaria a las 8:45 am)
# Ejecutar:  powershell -ExecutionPolicy Bypass -File instalar_tarea.ps1

$ErrorActionPreference = "Stop"

$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat = Join-Path $carpeta "resumen_diario.bat"

if (-not (Test-Path $bat)) {
    Write-Host "ERROR: no se encuentra $bat" -ForegroundColor Red
    exit 1
}

$nombreTarea = "ResumenCorreoDiario"

# Registrar la tarea: corre el .bat todos los dias a las 08:45
schtasks /Create /TN $nombreTarea /TR "`"$bat`"" /SC DAILY /ST 08:45 /F

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK. Tarea '$nombreTarea' creada: todos los dias a las 8:45 am." -ForegroundColor Green
    Write-Host "El resumen se guardara en tu Escritorio como 'resumen_diario.md'."
    Write-Host ""
    Write-Host "Para verificar:"
    Write-Host "  schtasks /Query /TN $nombreTarea"
    Write-Host ""
    Write-Host "Para eliminarla (si algun dia no la quieres):"
    Write-Host "  schtasks /Delete /TN $nombreTarea /F"
} else {
    Write-Host "ERROR al crear la tarea. Revisa el mensaje anterior." -ForegroundColor Red
    exit 1
}
