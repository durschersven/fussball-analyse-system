# fussball-analyse-system

Ein einfaches Fussball Analyse System als Ausgangspunkt für weitergehende Entwicklungen. Das Projekt erstellt automatisch eine SQLite Datenbank, kann CSV Dateien einlesen, ein Machine-Learning-Modell trainieren und Prognosen zu kommenden Spielen ausgeben. Vorhersagen werden gespeichert und nach Bekanntwerden der Ergebnisse ausgewertet, so dass das System seinen Lernerfolg kontrollieren kann. Inzwischen verwaltet die Datenbank auch Ligen und Saisons, so dass Daten mehrerer Wettbewerbe zusammengeführt werden können.

Die aktuelle Version berechnet zusätzlich Elo-Werte für Teams und verwendet diese bei der Prognose. Ein Kreuzvalidierungs-Schritt liefert einen realistischeren Eindruck der Modellqualität.

## Voraussetzungen

- Python 3.10+
- Abhängigkeiten aus `requirements.txt`

Installation der Abhängigkeiten:

```bash
pip install -r requirements.txt
```

## Nutzung

1. Datenbank initialisieren und CSV Daten laden:

```bash
python -m fussball_analyse.cli ingest teams path/zu/teams.csv
python -m fussball_analyse.cli ingest players path/zu/players.csv
python -m fussball_analyse.cli ingest matches path/zu/matches.csv
```

2. Modell trainieren und Prognosen berechnen:

```bash
python -m fussball_analyse.cli train
```

3. Kompletten Ablauf mit automatisch heruntergeladenen Daten testen:

```bash
python -m fussball_analyse.cli demo
```

Das Programm zeigt Trainingsgenauigkeit und Prognosen für Spiele ohne Ergebnis an. Eine echte selbstverbessernde Pipeline ist hier nur angedeutet und kann weiter ausgebaut werden.
Das Training speichert die Vorhersagen in der Datenbank. Sobald die realen Resultate eingetragen werden, misst das Programm automatisch die Trefferquote und nutzt die Daten bei jedem erneuten Aufruf von `train`, um das Modell neu zu trainieren.
Dabei fließen auch aktualisierte Elo-Werte der Teams ein. Die Konsole zeigt zusätzlich eine Kreuzvalidierungs-Genauigkeit an, um die Modellqualität einzuschätzen.

4. Aktuelle Ergebnisse mehrerer Ligen synchronisieren und danach trainieren:

```bash
python -m fussball_analyse.cli sync
python -m fussball_analyse.cli train
```

Der `sync`-Befehl lädt Premier League-, La-Liga- und Serie-A-Daten der neuesten
Saison direkt von *football-data.co.uk* herunter und legt sie in der Datenbank
an. Neue Ligen und Teams werden automatisch angelegt.
