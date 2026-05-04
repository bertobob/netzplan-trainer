import random
from domain.event import Event

# Typ-Alias: Ebenen-Index → Liste von Events
EventLevels = dict[int, list[Event]]


class Generator:
    """Erzeugt einen zufälligen Netzplan-Graphen."""

    MAX_EVENT_COUNT = 26
    MAX_SUCCESSOR_COUNT = 6
    MAX_EVENT_DURATION = 20

    def create_events(self, event_count: int, successor_count: int) -> tuple[EventLevels, int]:
        """
        Erstellt Events, verteilt sie auf Ebenen und verbindet sie.
        Gibt (events, hierarchie_count) zurück.
        """
        events, hierarchie_count = self._create_levels(event_count, successor_count)
        self._connect_levels(events, hierarchie_count)
        return events, hierarchie_count

    def _create_levels(self, event_count: int, successor_count: int) -> tuple[EventLevels, int]:
        """Erstellt Events und teilt sie zufällig auf Hierarchie-Ebenen auf."""
        events: EventLevels = {}
        hierarchie_count = 0
        current_level: list[Event] = []

        for i in range(event_count):
            event = Event(chr(ord("A") + i), random.randint(1, self.MAX_EVENT_DURATION))
            current_level.append(event)

            is_first       = i == 0
            is_second_last = i == event_count - 2
            is_last        = i == event_count - 1

            if is_first or is_second_last:
                events[hierarchie_count] = current_level
                hierarchie_count += 1
                current_level = []
            elif is_last:
                events[hierarchie_count] = current_level
            elif self._should_start_new_level(len(current_level), successor_count):
                events[hierarchie_count] = current_level
                hierarchie_count += 1
                current_level = []

        return events, hierarchie_count

    def _should_start_new_level(self, level_size: int, successor_count: int) -> bool:
        """Entscheidet probabilistisch ob eine neue Ebene beginnen soll."""
        prob = random.random()
        if level_size == 1:
            prob -= 0.8    # Ebene mit 1 Event nur selten
        elif level_size == 2:
            prob += 0.3    # 2 Events am wahrscheinlichsten
        return prob > 0.5 or level_size >= successor_count

    def _connect_levels(self, events: EventLevels, hierarchie_count: int) -> None:
        """Verbindet benachbarte Ebenen: jedes Event bekommt mind. einen Vor- und Nachfolger."""
        for i in range(hierarchie_count):
            unassigned = list(events[i + 1])

            for event in events[i]:
                if unassigned:
                    successor = random.choice(unassigned)
                    unassigned.remove(successor)
                else:
                    successor = random.choice(events[i + 1])
                event.add_child(successor)
                successor.add_parent(event)

            # Verbleibende Nachfolger ohne Vorgänger zuweisen
            for succ in unassigned:
                parent = random.choice(events[i])
                parent.add_child(succ)
                succ.add_parent(parent)
