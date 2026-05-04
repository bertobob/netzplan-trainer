from domain.event import Event

EventLevels = dict[int, list[Event]]
SolutionStep = dict[int, list[str]]


class Calculator:
    """
    Berechnet Vorwärts-/Rückwärtsterminierung, Puffer und Lösungsschritte.
    Kennt keine GUI – gibt nur Daten zurück.
    """

    def create_solutions(self, events: EventLevels, event_count: int) -> list[SolutionStep]:
        """Berechnet alle vier Lösungsschritte und gibt sie als Liste zurück."""
        return [
            self._build_empty_step(events),
            self._build_forward(events),
            self._build_backward(events, event_count),
            self._build_buffer(events),
        ]

    def _build_empty_step(self, events: EventLevels) -> SolutionStep:
        """Schritt 0: Leerer Startzustand – nur Event-Namen, alle Felder leer."""
        result = {}
        for index, event in self._iter_events(events):
            result[index] = ["", "", "", "", event.name, "", "", ""]
        return result

    def _build_forward(self, events: EventLevels) -> SolutionStep:
        """Schritt 1: Vorwärtsterminierung – FAZ und FEZ berechnen."""
        result = {}
        for index, event in self._iter_events(events):
            event.faz = 0 if event.is_start else max(p.fez for p in event.parents)
            event.fez = event.faz + event.duration
            result[index] = [str(event.faz), str(event.fez), "", "", event.name, str(event.duration), "", ""]
        return result

    def _build_backward(self, events: EventLevels, event_count: int) -> SolutionStep:
        """Schritt 2: Rückwärtsterminierung – SAZ und SEZ berechnen (von rechts nach links)."""
        result = {}
        index = event_count - 1

        for level_events in reversed(list(events.values())):
            level_result = {}
            for i, event in enumerate(level_events):
                if event.is_end:
                    event.saz = event.faz
                    event.sez = event.fez
                else:
                    event.sez = min(c.saz for c in event.children)
                    event.saz = event.sez - event.duration
                level_result[i] = [str(event.faz), str(event.fez), str(event.saz), str(event.sez),
                                   event.name, str(event.duration), "", ""]

            for items in reversed(list(level_result.values())):
                result[index] = items
                index -= 1
        return result

    def _build_buffer(self, events: EventLevels) -> SolutionStep:
        """Schritt 3: Puffer berechnen – GP und FP aus FAZ/FEZ/SAZ/SEZ ableiten."""
        result = {}
        for index, event in self._iter_events(events):
            event.gp = event.saz - event.faz
            event.fp = 0 if event.is_end else min(c.faz for c in event.children) - event.fez
            result[index] = [str(event.faz), str(event.fez), str(event.saz), str(event.sez),
                             event.name, str(event.duration), str(event.gp), str(event.fp)]
        return result

    def _iter_events(self, events: EventLevels):
        """Hilfsgenerator: liefert (index, event) über alle Ebenen."""
        index = 0
        for level_events in events.values():
            for event in level_events:
                yield index, event
                index += 1
