#!/usr/bin/env python3
import argparse
from pathlib import Path
from qr_core import generate_bulk_qr, make_qr, read_links_file


def run_cli(args: argparse.Namespace):
    links = []
    if args.input_file:
        fpath = Path(args.input_file)
        if not fpath.exists():
            print(f"El archivo de entrada no existe: {fpath}")
            raise SystemExit(1)
        links = list(read_links_file(fpath))
    else:
        links = args.urls or []

    if not links and not args.input_file:
        default_links = Path("links.txt")
        if default_links.exists():
            print("No se pasaron URLs: usando 'links.txt' en el directorio actual.")
            links = list(read_links_file(default_links))

    if not links:
        print("No se han proporcionado URLs. Usa --help para ver opciones.")
        raise SystemExit(1)

    if len(links) == 1 and args.output:
        out_path = Path(args.output)
        made = make_qr(links[0], out_path, box_size=args.box_size, border=args.border, image_format=args.format)
        print(f"Generado: {made}")
        return

    created = generate_bulk_qr(links, Path(args.out_dir), image_format=args.format)
    print("Generados:")
    for c in created:
        print(" -", c)


def run_gui():
    try:
        from qr_gui import run_gui_app
    except ImportError as exc:
        print("No se pudo abrir la interfaz PyQt6.")
        print("Instala dependencias con: pip install -r requirements.txt")
        print(f"Detalle: {exc}")
        raise SystemExit(1)

    raise SystemExit(run_gui_app())


def main():
    p = argparse.ArgumentParser(description="Genera codigos QR desde URL(s) y guarda imagenes.")
    p.add_argument("urls", nargs="*", help="URL(s) a convertir. Si se usa -i, se ignoran.")
    p.add_argument("-i", "--input-file", help="Archivo de texto con enlaces (una URL por linea).")
    p.add_argument("-o", "--output", help="Archivo de salida para un unico QR. Si se pasan varias URLs se usa -d.")
    p.add_argument("-d", "--out-dir", default="qrs", help="Directorio donde guardar los QR (por defecto: qrs)")
    p.add_argument("--box-size", type=int, default=10, help="Tamano de cada caja del QR (default 10)")
    p.add_argument("--border", type=int, default=4, help="Ancho del borde (default 4)")
    p.add_argument("--format", default="PNG", choices=["PNG", "JPEG"], help="Formato de salida (PNG o JPEG)")
    p.add_argument("--gui", action="store_true", help="Inicia la interfaz grafica.")
    args = p.parse_args()

    should_open_gui = args.gui or (not args.urls and not args.input_file and not args.output)
    if should_open_gui:
        run_gui()
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
