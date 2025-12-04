#!/usr/bin/env python3
"""
generate_qr.py
Genera códigos QR desde enlaces (uno o varios) y guarda imágenes PNG.

Uso:
  python generate_qr.py "https://ejemplo.com" -o mi_qr.png
  python generate_qr.py -i links.txt -d outdir

Dependencias: qrcode[pil], pillow
"""

import argparse
import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def safe_filename_from_url(url: str, ext: str = ".png") -> str:
    # Usa un hash corto para evitar caracteres inválidos en nombre de archivo
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(":", "_") or "link"
    return f"qr_{netloc}_{h}{ext}"


def make_qr(url: str, path: Path, box_size: int = 10, border: int = 4, error_correction=ERROR_CORRECT_M, image_format: str = "PNG"):
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format=image_format)
    return path


def read_links_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                yield s


def main():
    p = argparse.ArgumentParser(description="Genera códigos QR desde URL(s) y guarda imágenes PNG.")
    p.add_argument("urls", nargs="*", help="URL(s) a convertir. Si se usa -i, se ignoran.")
    p.add_argument("-i", "--input-file", help="Archivo de texto con enlaces (una URL por línea).")
    p.add_argument("-o", "--output", help="Archivo de salida para un único QR. Si se pasan varias URLs se usa -d.")
    p.add_argument("-d", "--out-dir", default="qrs", help="Directorio donde guardar los QR (por defecto: qrs)")
    p.add_argument("--box-size", type=int, default=10, help="Tamaño de cada caja del QR (default 10)")
    p.add_argument("--border", type=int, default=4, help="Ancho del borde (default 4)")
    p.add_argument("--format", default="PNG", choices=["PNG", "JPEG"], help="Formato de salida (PNG o JPEG)")
    args = p.parse_args()

    out_dir = Path(args.out_dir)

    links = []
    if args.input_file:
        fpath = Path(args.input_file)
        if not fpath.exists():
            print(f"El archivo de entrada no existe: {fpath}")
            raise SystemExit(1)
        links = list(read_links_file(fpath))
    else:
        links = args.urls or []

    # Si no se proporcionaron URLs ni -i, buscar automáticamente links.txt en el CWD
    if not links and not args.input_file:
        default_links = Path("links.txt")
        if default_links.exists():
            print("No se pasaron URLs: usando 'links.txt' en el directorio actual.")
            links = list(read_links_file(default_links))

    if not links:
        print("No se han proporcionado URLs. Usa --help para ver opciones.")
        raise SystemExit(1)

    # Si solo una URL y se pasó --output, usar ese nombre
    if len(links) == 1 and args.output:
        out_path = Path(args.output)
        try:
            made = make_qr(links[0], out_path, box_size=args.box_size, border=args.border, image_format=args.format)
            print(f"Generado: {made}")
            return
        except Exception as e:
            print(f"Error generando QR: {e}")
            raise

    # Si varias URLs o no se pasó -o, crear archivos en out_dir
    created = []
    for url in links:
        name = safe_filename_from_url(url, ext="." + args.format.lower())
        out_path = out_dir / name
        try:
            made = make_qr(url, out_path, box_size=args.box_size, border=args.border, image_format=args.format)
            created.append(str(made))
        except Exception as e:
            print(f"Error generando QR para {url}: {e}")

    if created:
        print("Generados:")
        for c in created:
            print(" - ", c)
    else:
        print("No se generó ningún QR.")


if __name__ == "__main__":
    main()
