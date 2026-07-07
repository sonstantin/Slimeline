# 🚇 Slimeline

Slimeline ist eine interaktive Desktop-Anwendung zum Planen, Erstellen und Verwalten von eigenen Verkehrsnetzwerken (z. B. U-Bahn- oder Busnetze). Die Anwendung wurde mit Python und Tkinter entwickelt und bietet eine grafische Oberfläche, mit der Stationen frei platziert, Linien gezogen, Fahrzeiten definiert und sogar optimale Routen inklusive Takt- und Wartezeiten berechnet werden können.

## ✨ Funktionen

* **🗺️ Freier Netzaufbau**: Stationen per Klick platzieren und flexibel miteinander zu Linien verknüpfen.
* **🔍 Integrierter Routenplaner**: Berechnet die schnellste Route zwischen zwei Stationen unter Berücksichtigung von realen Fahrzeiten und Takt-Wartezeiten am Bahnsteig.
* **🕒 Live-Fahrpläne**: Generiert dynamisch Abfahrtszeiten für jede Station (Vorwärts- und Rückwärtsrichtung) basierend auf dem Linientakt.
* **🚧 Baustellen-Management**: Bauprojekte an Stationen eintragen und verwalten, um Netzeinschränkungen zu simulieren.
* **🛠️ Bau-Modus**: Flexibles Umschalten zwischen dem Editier-Modus (Stationen setzen) und dem Interaktions-Modus (Fahrpläne einsehen).
* **🎨 Umfassende Personalisierung**: Linienfarben frei wählen, Linienbreiten anpassen sowie Hintergrundfarben für den Plan und die UI bestimmen.
* **📈 Parallele Linienführung**: Automatische Versatz-Berechnung (Spacing), wenn sich mehrere Linien dieselben Stationssegmente teilen.
* **📋 Listen & Suche**: Übersichtliche, durchsuchbare Listen aller Stationen und Linien für maximale Kontrolle auch bei Großnetzen.
* **💾 Speichern & Laden**: Das gesamte erstellte Verkehrsnetzwerk lässt sich unkompliziert als JSON-Datei sichern.
* **🌍 Mehrsprachigkeit**: Vorbereitung für Deutsch, Englisch und Latein sowie umschaltbares Zeitformat (1-24h / AM-PM).

## 📦 Verwendete Bibliotheken

Das Projekt verwendet folgende Python-Bibliotheken:
* `tkinter` (Grafische Benutzeroberfläche)
* `json` (Speichern und Laden von Plänen & Einstellungen)
* `PIL` / `Pillow` (Bildverarbeitung)
* `requests` (Automatischer Download des Programm-Icons)
* `pyperclip` (Fehler-Reporting in die Zwischenablage)
* `math`, `sys`, `os`, `datetime` (System- und Berechnungsfunktionen)

Installation der benötigten Pakete:
```bash
pip install pillow requests pyperclip

📁 Projektstruktur
Slimeline/
│
├── Linewidth.json           # Speichert Linienbreite, Sprache und Zeitformat
├── slimeline_text_*.json    # Sprachdateien (z.B. slimeline_text_Englisch.json)
├── Slimeline.png            # Programm-Icon (wird bei Bedarf automatisch geladen)
└── Slimeline_3.0.py         # Hauptanwendung

📝 Datenformat

Netzpläne werden als strukturierte JSON-Dateien gespeichert.
Beispiel für den inneren Aufbau:

{
    "lines": [
        [
            ["U1", 1, ["600"]],
            [[100, 150, "Hauptbahnhof"], [300, 150, "Marktplatz"]],
            [["120"]],
            "green"
        ]
    ],
    "stations": {
        "Hauptbahnhof": [100, 150],
        "Marktplatz": [300, 150]
    },
    "build": {
        "Hauptbahnhof": ["Gleiserneuerung"]
    }
}

⌨️ Tastenkombinationen (Shortcuts)

Für ein schnelles und effizientes Arbeiten lässt sich Slimeline fast vollständig über die Tastatur steuern:

    Escape : Anwendung beenden

    Strg + S : Netzplan speichern

    Strg + O : Netzplan laden

    Shift + Enter : Erstellung der aktuellen Linie abschließen

    Shift + Leertaste : Liste aller Stationen anzeigen

    Alt + Leertaste / Strg + Leer : Liste aller Verbindungen/Linien anzeigen

    Strg + U : Umsteigestopp über Namenseingabe hinzufügen

    Alt + C : Linienfarbe wählen

    Strg + B : Bau-Modus aktivieren/deaktivieren

    Strg + R : Routenplaner öffnen

    Strg + K : Komplexe Stationserstellung per Koordinaten (auch via Name /komplex)

    Shift + Escape : Alle Nebenfenster auf einmal schließen

    Strg + Shift + O / Alt + O : Einstellungsmenü öffnen

    Alt + R : Gesamten Plan zurücksetzen (Alles löschen)

    Pfeiltasten (bzw. WASD, falls aktiv) : Netzplan-Ausschnitt verschieben

🖥️ Features der Oberfläche

    Multi-Fenster-System: Detailmenüs für Stationen und Linien öffnen sich in übersichtlichen, separaten Fenstern (Toplevel).

    Fokus-Modus (Highlighting): Bei Auswahl einer Linie werden alle anderen Linien auf dem Canvas ausgegraut, um den Verlauf der ausgewählten Linie visuell hervorzuheben.

    Zweigeteilte Stationsnamen: Unterstützung für das |-Symbol im Stationsnamen, um zweizeilige Beschriftungen und Untertitel auf dem Plan zu erzeugen.

_Hinweis: Beim ersten Start versucht die Anwendung, ihr Icon von GitHub herunterzuladen und erstellt notwendige Konfigurationsdateien im lokalen Verzeichnis._
