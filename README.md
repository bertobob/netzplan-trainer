# Netzplan Trainer

Ein interaktives Desktop-Tool zum Üben der Netzplantechnik 

<img width="2550" height="1376" alt="grafik" src="https://github.com/user-attachments/assets/ff3f3793-2ce3-4e8d-8614-446cc9211237" />

---
# Netzplan Trainer

📥 Download der aktuellen Windows-Version:

https://github.com/bertobob/netzplan-trainer/releases/latest

## Über Netzplantechnik

Die Netzplantechnik ist ein Verfahren aus dem Projektmanagement zur Planung und Analyse von Vorgängen und deren Abhängigkeiten. Zur Übung müssen Netzpläne von Hand berechnet werden – mit Vorwärtsterminierung, Rückwärtsterminierung, Pufferzeiten und kritischem Pfad.

Existierende Tools zeigen entweder nur fertige Lösungen oder bieten keine interaktive Schritt-für-Schritt-Begleitung. Dieses Programm generiert zufällige Netzpläne und führt den Nutzer durch alle vier Berechnungsschritte.

---

## Features

- **Zufällige Netzplan-Generierung** – konfigurierbare Anzahl an Events und Ebenen
- **Schrittweise Lösung** – vier Lösungsschritte mit sofortigem Feedback
  1. Vorwärtsterminierung (FAZ / FEZ)
  2. Rückwärtsterminierung (SAZ / SEZ)
  3. Pufferberechnung (GP / FP)
  4. Kritischer Pfad (rot hervorgehoben)
- **Eingabe-Prüfung** – jeder Schritt wird einzeln auf Richtigkeit geprüft (grün / rot)
- **Musterlösung** – Lösung kann auf die Eingabefelder übertragen werden
- **Integrierte Anleitung** – erklärt alle Berechnungsschritte

---


---

## Architektur

Das Projekt ist in drei Schichten aufgeteilt:

```
netzplan/
  main.py           # Einstiegspunkt
  controller.py     # Verbindet Domain und GUI
  domain/
    event.py        # Datenmodell: ein Vorgang im Netzplan
    generator.py    # Zufällige Graph-Erzeugung
    calculator.py   # Terminierung und Pufferberechnung
  ui/
    gui.py          # Darstellung (PyQt6)
    input_canvas.py # Zeichenfläche für Verbindungslinien
  resources/
    stylesheet.qss
    info.html
```

`domain/` hat keine Abhängigkeit zu PyQt6 – die Fachlogik ist vollständig von der Darstellung getrennt.

---

## Installation

**Voraussetzungen:** Python 3.10+

```bash
git clone https://github.com/bertobob/netzplan-trainer.git
cd netzplan-trainer
pip install -r requirements.txt
python main.py
```

---

## Bedienung

1. Anzahl der Events und maximale Events pro Ebene einstellen
2. **Starte Übung** klicken – ein zufälliger Netzplan wird generiert
3. Werte in die Eingabefelder (oben) eintragen
4. Mit **Nächster Schritt** durch die vier Berechnungsschritte navigieren
5. **Prüfe Eingabe** zeigt welche Felder korrekt sind
6. **Übertrage Schritt** füllt die Musterlösung ein

---

## Technologien

- Python 3
- PyQt6
