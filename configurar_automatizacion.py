#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de la automatización del resumen de correo.
==========================================================

Pide el correo y la contraseña UNA sola vez (con entrada oculta) y los
guarda en "credenciales.txt" con permisos restringidos: solo tu usuario
de Windows puede leer ese archivo.

Después de ejecutarlo, el resumen diario programado podrá correr solo.

Uso:
  python configurar_automatizacion.py
"""

import getpass
import os
import subprocess
import sys

ARCHIVO = "credenciales.txt"


def _pedir_contrasena():
    for intento in range(3):
        try:
            contrasena = getpass.getpass("Tu contraseña (no se mostrará): ")
        except (EOFError, KeyboardInterrupt, OSError):
            contrasena = ""
        if contrasena:
            return contrasena
        print("  (No se recibió la contraseña. Inténtalo de nuevo.)", file=sys.stderr)
    print("Error: no se ingresó la contraseña.", file=sys.stderr)
    sys.exit(1)


def main():
    print("=" * 60)
    print(" Configurador de automatización del resumen de correo")
    print("=" * 60)
    print()
    print("Esto guardará tu correo y contraseña en un archivo local")
    print(f"llamado '{ARCHIVO}', en esta misma carpeta, para que el")
    print("resumen diario corra solo a las 8:00 am.")
    print()
    print("IMPORTANTE DE SEGURIDAD:")
    print("  - El archivo queda con permisos de SOLO TU USUARIO de Windows.")
    print("  - No compartas ese archivo ni esta carpeta con nadie.")
    print("  - Si quieres eliminar la automatización luego, borra el archivo")
    print(f"    '{ARCHIVO}' y elimina la tarea programada 'ResumenCorreoDiario'.")
    print()

    usuario = input("Tu correo institucional: ").strip()
    if not usuario:
        print("Error: no se indicó el correo.", file=sys.stderr)
        sys.exit(1)
    contrasena = _pedir_contrasena()

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(usuario + "\n")
        f.write(contrasena + "\n")

    _restringir_permisos()
    print()
    print(f"OK. Credenciales guardadas en: {os.path.abspath(ARCHIVO)}")
    print("Permisos restringidos aplicados (solo tu usuario puede leerlo).")
    print()
    print("Siguiente paso: registrar la tarea programada. Ejecuta:")
    print('  powershell -ExecutionPolicy Bypass -File instalar_tarea.ps1')


def _restringir_permisos():
    """En Windows, deja el archivo legible solo por el usuario actual."""
    if os.name != "nt":
        try:
            os.chmod(ARCHIVO, 0o600)
        except OSError:
            pass
        return
    try:
        subprocess.run(
            [
                "icacls", ARCHIVO,
                "/inheritance:r",
                "/grant:r", f"{os.environ['USERNAME']}:F",
            ],
            check=True,
            capture_output=True,
        )
    except (subprocess.SubprocessError, KeyError):
        print("Aviso: no se pudieron restringir los permisos automáticamente.", file=sys.stderr)
        print("Considera proteger el archivo manualmente (Propiedades > Seguridad).", file=sys.stderr)


if __name__ == "__main__":
    main()
