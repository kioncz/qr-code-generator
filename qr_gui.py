from pathlib import Path
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from qr_core import generate_bulk_qr, read_links_file


ICON_CANDIDATES = [
    Path(__file__).with_name("Qr-icon.png"),
    Path(__file__).parent / "assets" / "Qr-icon.png",
]


APP_STYLES = """
QWidget {
    background: #f4f6f8;
    color: #1f2937;
    font-family: 'Segoe UI';
    font-size: 14px;
}

QFrame#card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
}

QLabel#title {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
}

QLineEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #1f6feb;
}

QPushButton {
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    background: #e5e7eb;
    color: #111827;
    font-weight: 600;
}

QPushButton:hover {
    background: #dfe3e8;
}

QPushButton#primary {
    background: #0f766e;
    color: white;
}

QPushButton#primary:hover {
    background: #0d665f;
}

QMessageBox {
    background: #f4f6f8;
}

QMessageBox QLabel {
    color: #1f2937;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 88px;
    border: none;
    border-radius: 10px;
    padding: 8px 12px;
    background: #0f766e;
    color: white;
    font-weight: 600;
}

QMessageBox QPushButton:hover {
    background: #0d665f;
}
"""


class QRMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Generator")
        self.setMinimumSize(860, 580)
        self.app_icon = self._load_app_icon()
        if self.app_icon is not None:
            self.setWindowIcon(self.app_icon)

        self.output_dir = str(Path.cwd() / "qrs")
        self._build_ui()

    def _load_app_icon(self):
        for icon_path in ICON_CANDIDATES:
            if icon_path.exists():
                return QIcon(str(icon_path))
        return None

    def _show_message(self, level: str, title: str, message: str):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

        if self.app_icon is not None:
            dialog.setWindowIcon(self.app_icon)

        level_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "error": QMessageBox.Icon.Critical,
        }
        dialog.setIcon(level_map.get(level, QMessageBox.Icon.Information))
        dialog.exec()

    def _build_ui(self):
        root = QWidget()
        outer_layout = QVBoxLayout(root)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        title = QLabel("Generador de codigos QR")
        title.setObjectName("title")
        subtitle = QLabel("Agrega uno o varios enlaces y exporta PNG con nombres amigables.")
        subtitle.setStyleSheet("color:#4b5563;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        add_row = QHBoxLayout()
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://example.com")

        add_btn = QPushButton("Anadir")
        add_btn.clicked.connect(self.add_single_link)

        add_row.addWidget(self.link_input)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        self.links_text = QTextEdit()
        self.links_text.setPlaceholderText("Pega aqui varios links, uno por linea")
        layout.addWidget(self.links_text)

        tools_row = QHBoxLayout()
        load_btn = QPushButton("Cargar archivo de links")
        load_btn.clicked.connect(self.load_links_file)

        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self.links_text.clear)

        tools_row.addWidget(load_btn)
        tools_row.addWidget(clear_btn)
        tools_row.addStretch()
        layout.addLayout(tools_row)

        output_row = QHBoxLayout()
        self.output_input = QLineEdit(self.output_dir)

        choose_btn = QPushButton("Elegir carpeta")
        choose_btn.clicked.connect(self.choose_output_dir)

        output_row.addWidget(QLabel("Guardar en:"), alignment=Qt.AlignmentFlag.AlignVCenter)
        output_row.addWidget(self.output_input)
        output_row.addWidget(choose_btn)
        layout.addLayout(output_row)

        generate_btn = QPushButton("Generar QRs")
        generate_btn.setObjectName("primary")
        generate_btn.clicked.connect(self.generate_qrs)
        layout.addWidget(generate_btn)

        outer_layout.addWidget(card)
        self.setCentralWidget(root)

    def add_single_link(self):
        link = self.link_input.text().strip()
        if not link:
            self._show_message("warning", "Aviso", "Escribe un link antes de anadir.")
            return

        current = self.links_text.toPlainText().strip()
        if current:
            self.links_text.append(link)
        else:
            self.links_text.setPlainText(link)

        self.link_input.clear()

    def load_links_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona archivo de links",
            str(Path.cwd()),
            "Text files (*.txt);;All files (*.*)",
        )
        if not file_path:
            return

        links = list(read_links_file(Path(file_path)))
        if not links:
            self._show_message("info", "Info", "El archivo no contiene links validos.")
            return

        existing = self.links_text.toPlainText().strip()
        merged = "\n".join(links) if not existing else f"{existing}\n" + "\n".join(links)
        self.links_text.setPlainText(merged)

    def choose_output_dir(self):
        selected = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de guardado", self.output_input.text())
        if selected:
            self.output_input.setText(selected)

    def _collect_links(self) -> list[str]:
        raw = self.links_text.toPlainText()
        links = [line.strip() for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")]
        return links

    def generate_qrs(self):
        links = self._collect_links()
        if not links:
            self._show_message("error", "Error", "Debes agregar al menos un link.")
            return

        out_dir = self.output_input.text().strip()
        if not out_dir:
            self._show_message("error", "Error", "Selecciona una carpeta de salida.")
            return

        try:
            created = generate_bulk_qr(links, Path(out_dir), image_format="PNG")
        except Exception as exc:
            self._show_message("error", "Error", f"No se pudieron generar los QR:\n{exc}")
            return

        preview = "\n".join(path.name for path in created[:10])
        if len(created) > 10:
            preview += f"\n... y {len(created) - 10} archivo(s) mas"

        self._show_message(
            "info",
            "Listo",
            f"Se generaron {len(created)} QR(s) en:\n{out_dir}\n\nArchivos:\n{preview}",
        )


def run_gui_app() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLES)

    window = QRMainWindow()
    window.show()
    return app.exec()
