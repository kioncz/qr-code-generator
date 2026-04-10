from pathlib import Path
from urllib.parse import urlparse
import re

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    slug = slug.strip("-")
    return slug or "qr"


def friendly_filename_from_url(url: str, ext: str = ".png") -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    if not netloc:
        netloc = parsed.path.lower()

    netloc = netloc.replace("www.", "").split(":")[0]
    domain_name = netloc.split(".")[0] if "." in netloc else netloc
    base = slugify(domain_name or "qr")
    return f"{base}-qr{ext}"


def make_qr(
    url: str,
    path: Path,
    box_size: int = 10,
    border: int = 4,
    error_correction=ERROR_CORRECT_M,
    image_format: str = "PNG",
) -> Path:
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
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                yield clean


def deduplicate_filenames(names: list[str]) -> list[str]:
    used: dict[str, int] = {}
    result: list[str] = []

    for name in names:
        stem = Path(name).stem
        suffix = Path(name).suffix
        count = used.get(name, 0)

        if count == 0:
            result.append(name)
            used[name] = 1
            continue

        while True:
            candidate = f"{stem}-{count + 1}{suffix}"
            if candidate not in used:
                result.append(candidate)
                used[candidate] = 1
                used[name] = count + 1
                break
            count += 1

    return result


def generate_bulk_qr(links: list[str], out_dir: Path, image_format: str = "PNG") -> list[Path]:
    ext = "." + image_format.lower()
    names = deduplicate_filenames([friendly_filename_from_url(url, ext=ext) for url in links])

    created: list[Path] = []
    for url, name in zip(links, names):
        out_path = out_dir / name
        created.append(make_qr(url, out_path, image_format=image_format))

    return created
