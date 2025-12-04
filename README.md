# Generador de Códigos QR

Este es un sencillo pero práctico script de Python que genera códigos QR a partir de enlaces web. Fue creado como una herramienta útil para convertir rápidamente una o varias URLs en imágenes QR en formato PNG.

## Características

- **Generación individual:** Crea un código QR para un solo enlace.
- **Generación en lote:** Procesa un archivo de texto (`links.txt`) con múltiples enlaces para generar varios códigos QR a la vez.
- **Nombres automáticos:** Si no se especifica un nombre, el script asigna uno seguro basado en la URL.
- **Directorio de salida:** Permite organizar los códigos QR generados en un directorio específico.

## Tecnologías

- **Python**
- **qrcode[pil]:** La biblioteca principal para la creación de los QR.

## Uso Básico

1.  **Instalar dependencias:**
    ```powershell
    pip install -r requirements.txt
    ```

2.  **Generar un QR para un solo enlace:**
    ```powershell
    python generate_qr.py "https://github.com" -o mi_qr.png
    ```

3.  **Generar QR para una lista de enlaces:**
    Añade tus enlaces en `links.txt` y ejecuta:
    ```powershell
    python generate_qr.py -i links.txt -d qrs
    ```
    Las imágenes se guardarán en la carpeta `qrs/`.

