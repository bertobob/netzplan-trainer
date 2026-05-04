class Event:
    """Repräsentiert einen Vorgang (Knoten) im Netzplan."""

    def __init__(self, name: str, duration: int) -> None:
        self.name = name
        self.duration = duration
        self.parents: list["Event"] = []
        self.children: list["Event"] = []
        self.faz = 0   # Frühester Anfangszeitpunkt
        self.fez = 0   # Frühester Endzeitpunkt
        self.saz = 0   # Spätester Anfangszeitpunkt
        self.sez = 0   # Spätester Endzeitpunkt
        self.gp = 0    # Gesamtpuffer
        self.fp = 0    # Freier Puffer

    def add_child(self, child: "Event") -> None:
        if child not in self.children:
            self.children.append(child)

    def add_parent(self, parent: "Event") -> None:
        if parent not in self.parents:
            self.parents.append(parent)

    @property
    def is_start(self) -> bool:
        return not self.parents

    @property
    def is_end(self) -> bool:
        return not self.children

    def __repr__(self) -> str:
        return f"Event(name={self.name!r}, duration={self.duration})"
