"""
Tutor de equipos Thermo Fisher
Proyecto 3 - Automatiza algo tuyo con IA
Denis Rodriguez

Uso:
    python tutor_thermo.py            -> pide el numero de catalogo
    python tutor_thermo.py 1371       -> busca directo ese catalogo
HP88857198
El programa arma el link del producto en thermofisher.com con el numero de
catalogo, se lo pasa a Gemini (API gratis) para que lea la pagina y devuelve
la explicacion con las 6 preguntas. La respuesta se guarda en la carpeta "guias".
Tambien se puede pegar un link completo de Thermo Fisher en vez del numero.
"""

import os
import sys
import time
from datetime import datetime

from google import genai
from google.genai import types

# Carga la API key desde el archivo .env (si existe)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Modelos de Gemini con capa gratis. Si el primero falla se prueba el siguiente.
MODELOS = ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
CARPETA_GUIAS = "guias"
URL_PRODUCTO = "https://www.thermofisher.com/order/catalog/product/{}"

# Las mismas preguntas que use en la exploracion (caso 4)
INSTRUCCIONES = """Eres un tutor de equipos de laboratorio de Thermo Fisher Scientific.
Lee la pagina del producto que te paso. Quiero aprender a usarlo y entenderlo.
Con base en la pagina, dame:

0. Ficha: nombre del equipo, numero de catalogo y link de la pagina.
1. Para que sirve, explicado sencillo, como a alguien que nunca lo ha usado.
2. Como funciona por dentro (el principio cientifico) en maximo 5 lineas.
3. Las especificaciones mas importantes y que significa cada una en la practica (en tabla).
4. Pasos basicos para usarlo y errores comunes al usarlo.
5. Con que otros equipos o productos se usa normalmente.
6. 3 preguntas para comprobar que entendi, con sus respuestas.

Reglas:
- Usa solo la informacion de la pagina del producto. Si algo no esta en la pagina
  y lo agregas de tu conocimiento general, marcalo con "(no viene en la pagina)".
- No inventes especificaciones ni precios. Si el precio no aparece, escribe "pedir cotizacion".
- Si no pudiste abrir la pagina o no es un producto, dilo y no inventes el equipo.
- Responde en espanol y en formato Markdown."""


def armar_link(entrada):
    """Si me pasan un link lo uso tal cual, si no armo el link con el catalogo."""
    if entrada.startswith("http"):
        return entrada
    return URL_PRODUCTO.format(entrada)


def estado_paginas(respuesta):
    """Devuelve si Gemini pudo abrir la pagina (sirve para revisar errores)."""
    try:
        meta = respuesta.candidates[0].url_context_metadata
        return [f"{m.retrieved_url} -> {m.url_retrieval_status}" for m in meta.url_metadata]
    except (AttributeError, IndexError, TypeError):
        return []


def buscar_equipo(cliente, entrada):
    link = armar_link(entrada)
    pedido = f"Pagina del producto: {link}"
    config = types.GenerateContentConfig(
        system_instruction=INSTRUCCIONES,
        tools=[types.Tool(url_context=types.UrlContext())],
    )

    ultimo_error = None
    for modelo in MODELOS:
        for intento in range(1, 4):  # hasta 3 intentos por modelo
            try:
                respuesta = cliente.models.generate_content(
                    model=modelo, contents=pedido, config=config
                )
                return link, modelo, (respuesta.text or "").strip(), estado_paginas(respuesta)
            except Exception as e:  # modelo saturado, no existe o se acabo la cuota
                ultimo_error = e
                saturado = "503" in str(e) or "UNAVAILABLE" in str(e)
                print(f"  ({modelo}, intento {intento}: {str(e)[:80]}...)")
                if not saturado:
                    break  # si no es por saturacion, pasar al siguiente modelo
                time.sleep(5 * intento)  # esperar un poco y reintentar
    raise RuntimeError(f"Ningun modelo funciono: {ultimo_error}")


def guardar_guia(entrada, link, texto):
    os.makedirs(CARPETA_GUIAS, exist_ok=True)
    nombre = entrada if not entrada.startswith("http") else "link"
    fecha = datetime.now().strftime("%Y-%m-%d_%H%M")
    ruta = os.path.join(CARPETA_GUIAS, f"guia_{nombre}_{fecha}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"# Guia del equipo {entrada}\n\nFuente: {link}\n\n")
        f.write(texto + "\n")
    return ruta


def main():
    clave = os.environ.get("GEMINI_API_KEY")
    if not clave:
        print("Falta la API key. Crea un archivo .env con: GEMINI_API_KEY=tu_clave")
        sys.exit(1)

    cliente = genai.Client(api_key=clave)
    pendientes = sys.argv[1:]

    while True:
        if pendientes:
            entrada = pendientes.pop(0)
        else:
            entrada = input("\nNumero de catalogo o link (o 'salir'): ").strip()
        if entrada.lower() in ("salir", "s", ""):
            break

        print(f"Buscando {entrada} en thermofisher.com...")
        inicio = datetime.now()
        try:
            link, modelo, guia, estados = buscar_equipo(cliente, entrada)
        except RuntimeError as e:
            print(e)
            continue

        segundos = (datetime.now() - inicio).seconds
        print("\n" + "=" * 70)
        print(guia)
        print("=" * 70)
        for e in estados:
            print("Pagina leida:", e)
        ruta = guardar_guia(entrada, link, guia)
        print(f"Modelo: {modelo} | Guardado en {ruta} | Tardo {segundos} s")

        if not pendientes and len(sys.argv) > 1:
            break


if __name__ == "__main__":
    main()