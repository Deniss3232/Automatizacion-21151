# Tutor de equipos Thermo Fisher

Proyecto 3 - Automatiza algo tuyo con IA
Denis Rodríguez - 21151

Programa en Python que, con solo el número de catálogo de un producto de Thermo Fisher, abre la página del producto, se la pasa a Gemini y devuelve una guía para entenderlo: para qué sirve, cómo funciona, sus especificaciones, cómo se usa, con qué se usa y preguntas para repasar. Cada guía se guarda en la carpeta `guias`.

## Requisitos

- Python 3
- Una API key de Gemini (es gratis, se saca en Google AI Studio: https://aistudio.google.com)

## Cómo usarlo

1. Descargar o clonar el repositorio.

2. Instalar las librerías:

   ```
   pip install -r requirements.txt
   ```

   Esto instala `google-genai` (para conectarse con Gemini) y `python-dotenv` (para leer la clave).

3. Crear un archivo llamado `.env` en la misma carpeta, con esta línea:

   ```
   GEMINI_API_KEY=tu_clave
   ```

   El archivo `.env` no viene en el repositorio porque tiene la clave, cada quien tiene que poner la suya.

4. Correr el programa con el número de catálogo:

   ```
   python tutor_thermo.py 1371
   ```

   O sin número, para que lo vaya preguntando:

   ```
   python tutor_thermo.py
   ```

   Para salir se escribe `salir`.

## Carpetas

- `guias`: guías que generó el programa en las pruebas.
- `automatizacion documentos`: informe del proyecto.
