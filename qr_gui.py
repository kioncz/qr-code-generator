from pathlib import Path
import json
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QComboBox,
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
    QSpinBox,
)

from qr_core import generate_bulk_qr, read_links_file


ICON_CANDIDATES = [
    Path(__file__).with_name("Qr-icon.png"),
    Path(__file__).parent / "assets" / "Qr-icon.png",
]
LANG_DIR = Path(__file__).with_name("lang")


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
        self.setMinimumSize(860, 580)
        self.app_icon = self._load_app_icon()
        if self.app_icon is not None:
            self.setWindowIcon(self.app_icon)

        self.output_dir = str(Path.cwd() / "qrs")
        self.box_size = 10
        self.border = 4
        self.language = "es"
        self.translations = self._load_translation(self.language)
        self.setWindowTitle(self._text("window_title"))
        self._build_ui()

    def _load_translation(self, language: str) -> dict[str, str]:
        path = LANG_DIR / f"{language}.json"
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"No se pudo cargar el idioma '{language}': {exc}") from exc

    def _text(self, key: str) -> str:
        return self.translations[key]

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
        self.setWindowTitle(self._text("window_title"))
        root = QWidget()
        outer_layout = QVBoxLayout(root)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        title = QLabel(self._text("title"))
        title.setObjectName("title")
        subtitle = QLabel(self._text("subtitle"))
        subtitle.setStyleSheet("color:#4b5563;")


        layout.addWidget(title)
        layout.addWidget(subtitle)

        add_row = QHBoxLayout()
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText(self._text("link_placeholder"))

        add_btn = QPushButton(self._text("add"))
        add_btn.clicked.connect(self.add_single_link)

        add_row.addWidget(self.link_input)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        self.links_text = QTextEdit()
        self.links_text.setPlaceholderText(self._text("links_placeholder"))
        layout.addWidget(self.links_text)

        tools_row = QHBoxLayout()
        load_btn = QPushButton(self._text("load_links"))
        load_btn.clicked.connect(self.load_links_file)

        clear_btn = QPushButton(self._text("clear"))
        clear_btn.clicked.connect(self.links_text.clear)

        settings_btn = QPushButton(self._text("settings"))
        settings_btn.clicked.connect(self.open_settings)

        tools_row.addWidget(load_btn)
        tools_row.addWidget(clear_btn)
        tools_row.addStretch()
        tools_row.addWidget(settings_btn)
        layout.addLayout(tools_row)

        output_row = QHBoxLayout()
        self.output_input = QLineEdit(self.output_dir)

        choose_btn = QPushButton(self._text("choose_folder"))
        choose_btn.clicked.connect(self.choose_output_dir)

        output_row.addWidget(QLabel(self._text("save_to")), alignment=Qt.AlignmentFlag.AlignVCenter)
        output_row.addWidget(self.output_input)
        output_row.addWidget(choose_btn)
        layout.addLayout(output_row)

        generate_btn = QPushButton(self._text("generate"))
        generate_btn.setObjectName("primary")
        generate_btn.clicked.connect(self.generate_qrs)
        layout.addWidget(generate_btn)

        outer_layout.addWidget(card)
        self.setCentralWidget(root)

    def add_single_link(self):
        link = self.link_input.text().strip()
        if not link:
            self._show_message("warning", self._text("warning_title"), self._text("no_link_warning"))
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
            self._text("load_links"),
            str(Path.cwd()),
            self._text("links_file_filter"),
        )
        if not file_path:
            return

        links = list(read_links_file(Path(file_path)))
        if not links:
            self._show_message("info", self._text("info_title"), self._text("info_description"))
            return

        existing = self.links_text.toPlainText().strip()
        merged = "\n".join(links) if not existing else f"{existing}\n" + "\n".join(links)
        self.links_text.setPlainText(merged)

    def choose_output_dir(self):
        selected = QFileDialog.getExistingDirectory(self, self._text("select_folder"), self.output_input.text())
        if selected:
            self.output_input.setText(selected)

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._text("settings_title"))
        dialog.setWindowIcon(self.app_icon or QIcon())

        form = QFormLayout(dialog)
        box_size_input = QSpinBox()
        box_size_input.setRange(1, 50)
        box_size_input.setValue(self.box_size)
        box_size_input.setToolTip(self._text("qr_size_tip"))

        border_input = QSpinBox()
        border_input.setRange(0, 20)
        border_input.setValue(self.border)
        border_input.setToolTip(self._text("margin_tip"))

        form.addRow(self._text("qr_size"), box_size_input)
        form.addRow(self._text("margin"), border_input)

        language_input = QComboBox()
        language_input.addItem(self._text("spanish"), "es")
        language_input.addItem(self._text("english"), "en")
        language_input.setCurrentIndex(language_input.findData(self.language))
        form.addRow(self._text("language"), language_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.box_size = box_size_input.value()
            self.border = border_input.value()
            selected_language = language_input.currentData()
            if selected_language != self.language:
                links = self.links_text.toPlainText()
                output_dir = self.output_input.text()
                self.language = selected_language
                self.translations = self._load_translation(self.language)
                self._build_ui()
                self.links_text.setPlainText(links)
                self.output_input.setText(output_dir)

    def _collect_links(self) -> list[str]:
        raw = self.links_text.toPlainText()
        links = [line.strip() for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")]
        return links

    def generate_qrs(self):
        links = self._collect_links()
        if not links:
            self._show_message("error", self._text("error_title"), self._text("no_links"))
            return

        out_dir = self.output_input.text().strip()
        if not out_dir:
            self._show_message("error", self._text("error_title"), self._text("no_output_dir"))
            return

        try:
            created = generate_bulk_qr(
                links,
                Path(out_dir),
                image_format="PNG",
                box_size=self.box_size,
                border=self.border,
            )
        except Exception as exc:
            self._show_message(
                "error",
                self._text("error_title"),
                self._text("error_generating_qr").format(error=str(exc)),
            )
            return

        preview = "\n".join(path.name for path in created[:10])
        if len(created) > 10:
            preview += f"\n... {len(created) - 10} {self._text('more_files')}"

        self._show_message(
            "info",
            self._text("generation_complete"),
            f"{self._text('generated')} {len(created)} {self._text('qrs_in')}\n"
            f"{out_dir}\n\n{self._text('files')}\n{preview}",
        )


def run_gui_app() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLES)

    window = QRMainWindow()
    window.show()
    return app.exec()
