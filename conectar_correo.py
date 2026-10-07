#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conector de correo institucional (Zimbra)
==========================================

Se conecta al servidor de correo de la institución (mail.cooperco.fin.ec)
vía IMAP cifrado (SSL, puerto 993) y permite:

  --listar N    Mostrar los últimos N correos de una carpeta (remitente,
                asunto, fecha, cantidad de adjuntos).
  --adjuntos N  Descargar los adjuntos de los últimos N correos a la
                carpeta "Adjuntos/".
  --reporte     Generar un archivo CSV con los datos de los últimos N
                correos (remitente, asunto, fecha, adjuntos).
  --leidos N    Listar los últimos N correos y marcar como leídos SOLO
                los que tú elijas (con confirmación antes de aplicar).
  --resumen N   Resumen de correos importantes: detecta los mensajes
                personalizados (con tu nombre en el saludo o asunto),
                los clasifica por prioridad/tipo/acción con reglas locales
                (sin IA externa) y descarta los masivos/boletines; lo
                imprime y lo guarda en "resumen.md" / "resumen.html".

La contraseña se pide al ejecutar con entrada oculta; nunca se guarda ni
se transmite fuera de tu equipo. La lectura usa BODY.PEEK (no marca
mensajes como leídos por sí sola); el único modo que modifica tu correo
es --leidos, y solo marca lo que tú confirmes.

Ejemplos:
  python conectar_correo.py --listar 20
  python conectar_correo.py --adjuntos 20
  python conectar_correo.py --reporte --n 50
  python conectar_correo.py --leidos 20
  python conectar_correo.py --resumen 100
  python conectar_correo.py --usuario tu@cooperco.fin.ec --listar
  python conectar_correo.py --carpeta Sent --listar 10
"""

import argparse
import csv
import datetime
import email
import getpass
import html as html_mod
import imaplib
import json
import os
import re
import socket
import ssl
import sys
import unicodedata
from email.header import decode_header
from email.utils import parsedate_to_datetime

SERVIDOR = "mail.cooperco.fin.ec"
PUERTO = 993
CARPETA_ADJUNTOS = "Adjuntos"
REPORTE = "reporte_correos.csv"
RESUMEN = "resumen.md"
RESUMEN_HTML = "resumen.html"
ESTADO_RESUMEN = "estado_resumen.json"
IMPORTANTES_ACUMULADOS = "importantes_acumulados.json"

VENTANA_CUERPO = 3000

PALABRAS_URGENTE = [
    "urgente", "urgencia", "de inmediato", "respuesta inmediata",
    "hoy", "antes de hoy", "prioridad", "vencimiento proximo",
    "requiere correccion", "incidente", "bloqueo", "bloqueado",
    "bloqueada", "caido", "caida", "fuera de servicio",
]

PALABRAS_ALTA = [
    "requiere respuesta", "aprobacion", "aprobar", "validacion", "validar",
    "revision", "revisar", "autorizacion", "autorizar", "entrega pendiente",
    "solicitud formal", "requerimiento", "gerencia", "jefatura",
]

PALABRAS_MEDIA = [
    "seguimiento", "consulta", "coordinacion", "documento recibido",
    "documentos recibidos", "informacion adicional",
]

PALABRAS_INFORMATIVA_FORZADA = [
    "felicidades", "feliz cumpleanos", "cumpleanos", "boletin",
    "comunicado general", "aniversario",
]

VERBOS_ACCION = [
    "revis", "valid", "aprob", "aprueb", "confirm", "envi", "respond",
    "correg", "corrig", "coordin", "adjunt", "remit", "complet", "verific",
    "autoriz", "atend", "atiend", "gestion"
]

# Archivo truncado aquí solo para evitar inventar contenido: el repositorio debe reflejar exactamente el ZIP subido.
