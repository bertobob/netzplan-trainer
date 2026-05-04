from domain.generator import Generator
from domain.calculator import Calculator

SOLUTION_STEPS = 4

# Welche Widget-Felder (Index) welchem Event-Attribut entsprechen – je Lösungsschritt
SOLUTION_FIELDS = {
    1: [(0, "faz"), (1, "fez"), (4, "duration")],
    2: [(0, "faz"), (1, "fez"), (2, "saz"), (3, "sez"), (4, "duration")],
    3: [(0, "faz"), (1, "fez"), (2, "saz"), (3, "sez"), (4, "duration"), (5, "gp"), (6, "fp")],
}

STEP_NAMES = {
    1: "Vorwärtsterminierung",
    2: "Rückwärtsterminierung",
    3: "Pufferberechnung",
    4: "Kritischer Pfad",
}

MAX_EVENT_COUNT    = 26
MAX_SUCCESSOR_COUNT = 6


class NetzplanController:
    """
    Verbindet Domain und GUI.
    Kennt beide Seiten, aber hält sie voneinander getrennt.
    """

    def __init__(self, gui=None) -> None:
        self.gui = gui
        self.generator = Generator()
        self.calculator = Calculator()

        self.event_count = 9
        self.successor_count = 3
        self.output_index = 0
        self.events = {}
        self.hierarchie_count = 0
        self.solutions = []
        self.widget_height = 20
        self.widget_width = 30

    # ------------------------------------------------------------------
    # Eingabe-Validierung
    # ------------------------------------------------------------------

    def validate_input(self, attr_name: str, widget, inc_dec: int, is_entered: bool) -> None:
        limits = {"event_count": MAX_EVENT_COUNT, "successor_count": MAX_SUCCESSOR_COUNT}
        hi = limits[attr_name]

        if is_entered:
            text = widget.text()
            if text.isdigit() and 0 < int(text) <= hi:
                setattr(self, attr_name, int(text))
                widget.setStyleSheet("background-color: lightblue;")
            else:
                widget.setStyleSheet("background-color: lightcoral;")
        else:
            new_value = max(1, min(hi, getattr(self, attr_name) + inc_dec))
            setattr(self, attr_name, new_value)
            widget.setText(str(new_value))

    # ------------------------------------------------------------------
    # Übungs-Steuerung
    # ------------------------------------------------------------------

    def start_exercise(self) -> None:
        self.gui.values = {}
        self.events, self.hierarchie_count = self.generator.create_events(
            self.event_count, self.successor_count
        )
        self.solutions = self.calculator.create_solutions(self.events, self.event_count)

        self.gui.fill_table(self.events)
        self.gui.show_input_events(self.events, self.hierarchie_count, self.widget_width, self.widget_height)
        self.gui.draw_connections(self.gui.input_canvas, self.events, self.widget_width, self.widget_height)

        self.output_index = 0
        self._render_output()
        self._update_check_button_label()

    def process_button(self, index: int) -> None:
        match index:
            case 0:  # Vorheriger Schritt
                if self.output_index > 0:
                    self.output_index -= 1
                self._render_output()
            case 1:  # Nächster Schritt
                if self.output_index < SOLUTION_STEPS:
                    self.output_index += 1
                self._render_output()
            case 2:
                self.gui.show_info()
            case 3:
                if self.output_index != 0:
                    self._check_input()
            case 4:
                if self.output_index != 0:
                    self._broadcast_output()
        self._update_check_button_label()

    def _render_output(self) -> None:
        """Übergibt den aktuellen Lösungsschritt an die GUI zum Rendern."""
        step = SOLUTION_STEPS - 1 if self.output_index == SOLUTION_STEPS else self.output_index
        self.gui.show_output_events(
            self.solutions[step], self.events, self.hierarchie_count,
            self.widget_width, self.widget_height
        )
        self.gui.draw_connections(self.gui.output_canvas, self.events, self.widget_width, self.widget_height)
        if self.output_index == SOLUTION_STEPS:
            self.gui.draw_critical(self.events, self.hierarchie_count, self.widget_width, self.widget_height)

    # ------------------------------------------------------------------
    # Eingabe-Prüfung & Übertragung
    # ------------------------------------------------------------------

    def _get_active_step(self) -> int:
        return SOLUTION_STEPS - 1 if self.output_index == SOLUTION_STEPS else self.output_index

    def _find_event(self, name: str):
        for level_events in self.events.values():
            for event in level_events:
                if event.name == name:
                    return event
        return None

    def _check_input(self) -> None:
        """Vergleicht Nutzereingaben mit der Musterlösung – grün = richtig, rot = falsch."""
        step = self._get_active_step()
        fields = SOLUTION_FIELDS[step]
        for event_name, widgets in self.gui.values.items():
            event = self._find_event(event_name)
            if event is None:
                continue
            for widget_idx, attr_name in fields:
                is_correct = widgets[widget_idx].text() == str(getattr(event, attr_name))
                color = "lightgreen" if is_correct else "lightcoral"
                widgets[widget_idx].setStyleSheet(f"background-color: {color};")

    def _broadcast_output(self) -> None:
        """Überträgt die Musterlösung in die Eingabefelder."""
        step = self._get_active_step()
        fields = SOLUTION_FIELDS[step]
        for event_name, widgets in self.gui.values.items():
            event = self._find_event(event_name)
            if event is None:
                continue
            for widget_idx, attr_name in fields:
                widgets[widget_idx].setText(str(getattr(event, attr_name)))

    def _update_check_button_label(self) -> None:
        """Aktualisiert den 'Prüfe Eingabe'-Button mit dem aktuellen Schrittnamen."""
        step_name = STEP_NAMES.get(self.output_index, "")
        label = f"Prüfe Eingabe: {step_name}" if step_name else "Prüfe Eingabe"
        self.gui.buttons[3].setText(label)
