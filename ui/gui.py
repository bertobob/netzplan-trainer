import sys
import os
from pathlib import Path

from ui.input_canvas import InputCanvas
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit, QLabel,
    QGridLayout, QVBoxLayout, QSizePolicy, QTableWidget,
    QHBoxLayout, QMessageBox, QDialog, QTextEdit, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt


def get_resource_path(relative_path: str) -> Path:
    """Gibt den korrekten Pfad zurück – auch wenn als EXE gebundelt."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent / "resources"
    return base / relative_path


class Gui(QWidget):
    """
    Haupt-GUI des Netzplan-Trainers.
    Verantwortlich für Darstellung – kennt keine Domain-Logik.
    Bekommt alle Daten vom Controller übergeben.
    """

    BUTTON_LABELS = [
        "Vorheriger Schritt",
        "Nächster Schritt",
        "Info",
        "Prüfe Eingabe",
        "Übertrage Schritt auf Eingabe",
    ]

    def __init__(self, controller=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.values: dict[str, list[QLineEdit]] = {}
        self.widget_list: dict[str, list] = {}
        self.widget_list_output: dict[str, list] = {}
        self.buttons: list[QPushButton] = []

        self._init_window()
        self._init_left_panel()
        self._init_right_panel()
        self._load_stylesheet()
        self.show()

    # ------------------------------------------------------------------
    # Initialisierung
    # ------------------------------------------------------------------

    def _init_window(self) -> None:
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(screen_geometry.width(), screen_geometry.height())
        self.setWindowTitle("Netzplan Trainer")

        self.main_layout = QGridLayout()
        self.main_layout.setColumnStretch(0, 2)
        self.main_layout.setColumnStretch(1, 10)
        self.setLayout(self.main_layout)

    def _init_left_panel(self) -> None:
        """Linke Sidebar: Eingabefelder, Start-Button, Tabelle."""
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        inner = QGridLayout()

        inner.addWidget(QLabel("Anzahl Events"), 0, 0)
        self.event_count = QLineEdit("9", placeholderText="Anzahl Events")
        self.event_count.setToolTip("Anzahl der Events eingeben, höchstens 26")
        self.event_count.textChanged.connect(
            lambda: self.controller.validate_input("event_count", self.event_count, 0, True)
        )
        inner.addWidget(self.event_count, 1, 0)
        self._add_spinner_buttons(inner, row=1, attr="event_count", field=self.event_count)

        inner.addWidget(QLabel("Max. Events/Ebene"), 2, 0)
        self.successor_count = QLineEdit("3", placeholderText="Max Nachfolger")
        self.successor_count.setToolTip("Wieviel Events/Ebene, mehr als 3 sind schlecht lesbar")
        self.successor_count.textChanged.connect(
            lambda: self.controller.validate_input("successor_count", self.successor_count, 0, True)
        )
        inner.addWidget(self.successor_count, 3, 0)
        self._add_spinner_buttons(inner, row=3, attr="successor_count", field=self.successor_count)

        self.go_button = QPushButton("Starte Übung")
        self.go_button.setObjectName("go_button")
        self.go_button.clicked.connect(self.controller.start_exercise)
        inner.addWidget(self.go_button, 4, 0)

        self.table = QTableWidget(26, 3)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setHorizontalHeaderLabels(["Event", "Dauer", "Nachfolger"])
        inner.addWidget(self.table, 5, 0, 1, 3)

        left_layout.addLayout(inner)
        container = QWidget()
        container.setLayout(left_layout)
        self.main_layout.addWidget(container, 0, 0)

    def _add_spinner_buttons(self, layout, row, attr, field) -> None:
        plus = QPushButton("+")
        plus.setObjectName("incr_button")
        plus.clicked.connect(lambda: self.controller.validate_input(attr, field, 1, False))
        layout.addWidget(plus, row, 1)

        minus = QPushButton("-")
        minus.setObjectName("incr_button")
        minus.clicked.connect(lambda: self.controller.validate_input(attr, field, -1, False))
        layout.addWidget(minus, row, 2)

    def _init_right_panel(self) -> None:
        """Rechter Bereich: Input-Canvas, Buttons, Output-Canvas."""
        right_layout = QGridLayout()
        right_layout.setRowStretch(0, 10)
        right_layout.setRowStretch(1, 1)
        right_layout.setRowStretch(2, 10)

        self.input_canvas = InputCanvas()
        self.input_canvas.setObjectName("input_canvas")
        self.output_canvas = InputCanvas()
        self.output_canvas.setObjectName("output_canvas")

        button_row = QHBoxLayout()
        for i, label in enumerate(self.BUTTON_LABELS):
            button = QPushButton(label)
            button.setObjectName("go_button")
            button.clicked.connect(lambda checked, idx=i: self.controller.process_button(idx))
            self.buttons.append(button)
            button_row.addWidget(button)

        right_layout.addWidget(self.input_canvas, 0, 0)
        right_layout.addLayout(button_row, 1, 0)
        right_layout.addWidget(self.output_canvas, 2, 0)
        self.main_layout.addLayout(right_layout, 0, 1)

    def _load_stylesheet(self) -> None:
        path = get_resource_path("stylesheet.qss")
        try:
            self.setStyleSheet(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"Warnung: stylesheet.qss nicht gefunden ({path})")

    # ------------------------------------------------------------------
    # Rendering – bekommt Daten vom Controller
    # ------------------------------------------------------------------

    def fill_table(self, events: dict) -> None:
        """Füllt die Tabelle mit Event-Namen, Dauer und Nachfolgern."""
        self.table.clearContents()
        row = 0
        for level_events in events.values():
            for event in level_events:
                self.table.setItem(row, 0, QTableWidgetItem(event.name))
                self.table.setItem(row, 1, QTableWidgetItem(str(event.duration)))
                successors = " ".join(c.name for c in event.children)
                self.table.setItem(row, 2, QTableWidgetItem(successors))
                row += 1

    def show_input_events(self, events: dict, hierarchie_count: int, width: int, height: int) -> None:
        """Rendert die editierbaren Eingabe-Knoten auf dem Input-Canvas."""
        self._clear_canvas(self.input_canvas)
        self.widget_list.clear()
        canvas_w = self.input_canvas.width()
        canvas_h = self.input_canvas.height()
        for level, level_events in events.items():
            y_offset = canvas_h // (len(level_events) + 1)
            for i, event in enumerate(level_events):
                x = int(canvas_w / hierarchie_count * level * 0.9)
                y = (i + 1) * y_offset - 4 * height
                self._render_input_node(event.name, x, y, width, height)

    def show_output_events(self, solution_step: dict, events: dict, hierarchie_count: int, width: int, height: int) -> None:
        """Rendert die Lösungs-Knoten auf dem Output-Canvas."""
        self._clear_canvas(self.output_canvas)
        self.widget_list_output.clear()
        canvas_w = self.output_canvas.width()
        canvas_h = self.output_canvas.height()

        # Legende
        self._render_output_node(["FAZ", "FEZ", "SAZ", "SEZ", "ID", "DUR", "GP", "FP"], 0, 0, width, height)

        index = 0
        for level, level_events in events.items():
            y_offset = canvas_h // (len(level_events) + 1)
            for i, event in enumerate(level_events):
                x = int(canvas_w / hierarchie_count * level * 0.9)
                y = (i + 1) * y_offset - 4 * height
                self._render_output_node(solution_step[index], x, y, width, height)
                index += 1

    def draw_connections(self, canvas: InputCanvas, events: dict, width: int, height: int) -> None:
        """Zeichnet schwarze Verbindungslinien zwischen den Knoten."""
        for level_events in events.values():
            for event in level_events:
                for child in event.children:
                    x1 = self.widget_list[event.name][4].x() + 2 * width
                    y1 = self.widget_list[event.name][4].y() + height
                    x2 = self.widget_list[child.name][3].x()
                    y2 = self.widget_list[child.name][3].y() + height
                    canvas.add_line(x1, y1, x2, y2, (0, 0, 0))

    def draw_critical(self, events: dict, hierarchie_count: int, width: int, height: int) -> None:
        """Zeichnet den kritischen Pfad in Rot (GP=0 und FP=0)."""
        self.output_canvas.remove_lines()
        event = events[0][0]
        for _ in range(hierarchie_count):
            next_event = next((c for c in event.children if c.gp == 0 and c.fp == 0), None)
            if next_event is None:
                break
            x1 = self.widget_list[event.name][4].x() + 2 * width
            y1 = self.widget_list[event.name][4].y() + height
            x2 = self.widget_list[next_event.name][3].x()
            y2 = self.widget_list[next_event.name][3].y() + height
            self.output_canvas.add_line(x1, y1, x2, y2, (255, 0, 0))
            event = next_event

    # ------------------------------------------------------------------
    # Knoten-Rendering (intern)
    # ------------------------------------------------------------------

    def _render_input_node(self, node_id: str, xpos: int, ypos: int, width: int, height: int) -> None:
        """Erstellt einen editierbaren Knoten auf dem Input-Canvas."""
        faz = QLineEdit(); faz.setObjectName("input_no_border")
        fez = QLineEdit(); fez.setObjectName("input_no_border")
        saz = QLineEdit(); saz.setObjectName("input_no_border")
        sez = QLineEdit(); sez.setObjectName("input_no_border")
        d   = QLineEdit(); d.setObjectName("input_border")
        gp  = QLineEdit(); gp.setObjectName("input_border")
        fp  = QLineEdit(); fp.setObjectName("input_border")

        self.values[node_id] = [faz, fez, saz, sez, d, gp, fp]

        blank1 = QLabel(""); blank1.setObjectName("blank_field")
        blank2 = QLabel(""); blank2.setObjectName("blank_field")
        ids    = QLabel(node_id); ids.setObjectName("label_border")
        label  = QLabel("Event"); label.setObjectName("label_border")

        widgets = [faz, blank1, fez, ids, label, d, gp, fp, saz, blank2, sez]
        self.widget_list[node_id] = widgets
        self._place_widgets(widgets, self.input_canvas, xpos, ypos, width, height)

    def _render_output_node(self, data: list[str], xpos: int, ypos: int, width: int, height: int) -> None:
        """Erstellt einen nicht-editierbaren Lösungs-Knoten auf dem Output-Canvas."""
        faz = QLabel(data[0]); faz.setObjectName("input_no_border")
        fez = QLabel(data[1]); fez.setObjectName("input_no_border")
        saz = QLabel(data[2]); saz.setObjectName("input_no_border")
        sez = QLabel(data[3]); sez.setObjectName("input_no_border")
        ids = QLabel(data[4]); ids.setObjectName("label_border")
        d   = QLabel(data[5]); d.setObjectName("input_border")
        gp  = QLabel(data[6]); gp.setObjectName("input_border")
        fp  = QLabel(data[7]); fp.setObjectName("input_border")

        blank1 = QLabel(""); blank1.setObjectName("blank_field")
        blank2 = QLabel(""); blank2.setObjectName("blank_field")
        label  = QLabel("Event"); label.setObjectName("label_border")

        widgets = [faz, blank1, fez, ids, label, d, gp, fp, saz, blank2, sez]
        self.widget_list_output[data[4]] = widgets
        self._place_widgets(widgets, self.output_canvas, xpos, ypos, width, height)

    def _place_widgets(self, widgets: list, canvas: QWidget, xpos: int, ypos: int, width: int, height: int) -> None:
        """Positioniert die 11 Teil-Widgets eines Knotens im 3×4 Raster."""
        index = 0
        for row in range(4):
            col = 0
            while col < 3:
                w = widgets[index]
                w.setParent(canvas)
                if index == 4:  # Label-Feld ist doppelt breit
                    w.setGeometry(xpos + col * width + 2, ypos + row * height + row * 2, width * 2, height)
                    col += 1
                else:
                    w.setGeometry(xpos + col * width + 2, ypos + row * height + row * 2, width, height)
                w.show()
                index += 1
                col += 1

    # ------------------------------------------------------------------
    # Canvas-Verwaltung
    # ------------------------------------------------------------------

    def _clear_canvas(self, canvas: InputCanvas) -> None:
        for widget in canvas.findChildren(QWidget):
            widget.deleteLater()
            widget.setParent(None)
        canvas.remove_lines()

    # ------------------------------------------------------------------
    # Info-Dialog
    # ------------------------------------------------------------------

    def show_info(self) -> None:
        path = get_resource_path("info.html")
        try:
            html = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            QMessageBox.warning(self, "Fehler", f"Hilfedatei nicht gefunden:\n{path}")
            return
        popup = QDialog(self)
        popup.setWindowTitle("Netzplan-Trainer Anleitung")
        popup.resize(1000, 1000)
        layout = QVBoxLayout(popup)
        text_edit = QTextEdit(popup)
        text_edit.setReadOnly(True)
        text_edit.setHtml(html)
        layout.addWidget(text_edit)
        popup.exec()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
