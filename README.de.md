<div align="center">
  <h1>Bear Blog Skill</h1>
  <p><b>Bear Blog mit einem Agenten oder einer kleinen Python-CLI verwalten.</b></p>
  <p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <b>Deutsch</b></p>
  <p>
    <a href="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml"><img src="https://github.com/somkanel/bearblog-skill/actions/workflows/checks.yml/badge.svg" alt="Checks"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
  </p>
</div>

Ein Agent Skill für **Codex, Claude Code und kompatible Werkzeuge**, mit einem eigenständig nutzbaren Python-Client für die [Bear Blog API](https://docs.bearblog.dev/api/).

- Beiträge und Seiten erstellen, bearbeiten, veröffentlichen, planen und löschen.
- Startseite, Navigation, CSS und unterstützte Blog-Einstellungen ändern.
- Entwürfe und geplante Beiträge auflisten, vollständige Inhalte abrufen und API-Daten exportieren.

## Voraussetzungen

Python 3.9+, ein Bear Blog mit kostenpflichtigem Upgrade und ein API-Schlüssel aus **Dashboard → Settings → API**. Auch bei eigener Domain wird die ursprüngliche Bear-Subdomain verwendet. Die Skripte benötigen nur die Python-Standardbibliothek; macOS und Linux werden unterstützt.

## Installation

Mit [Skills CLI](https://github.com/vercel-labs/skills), Node.js/npm und Git:

```bash
npx skills add somkanel/bearblog-skill --skill bearblog -a codex claude-code -g
```

Nach `-a` nur den verwendeten Agenten angeben. Ohne `-g` erfolgt die Installation im Projekt. Nach der Installation eine neue Unterhaltung öffnen.

<details>
<summary>Manuelle Installation</summary>

```bash
git clone https://github.com/somkanel/bearblog-skill.git
```

Das Repository klonen und das vollständige Verzeichnis `skills/bearblog` an den passenden Ort kopieren. Eigene Anpassungen vor dem Ersetzen einer vorhandenen Installation sichern.

| Agent | Skill-Verzeichnis des Benutzers |
| --- | --- |
| Codex | `~/.agents/skills/bearblog` |
| Claude Code | `~/.claude/skills/bearblog` |

</details>

## Konfiguration

Im Terminal `SKILL_DIR` auf das installierte Verzeichnis setzen. Für eine globale Codex-Standardinstallation:

```bash
SKILL_DIR="$HOME/.agents/skills/bearblog"
python3 "$SKILL_DIR/scripts/bearblog.py" configure
python3 "$SKILL_DIR/scripts/bearblog.py" get-blog
```

Für Claude Code `~/.claude/skills/bearblog` verwenden, in einem Repository-Klon `./skills/bearblog`. Der Befehl fragt Subdomain und API-Schlüssel mit verdeckter Eingabe ab und speichert `~/.config/bearblog/config.json` mit POSIX-Rechten `0600`. `get-blog` prüft den Zugriff, ohne den Blog zu ändern.

Für Automatisierung **beide** Umgebungsvariablen `BEARBLOG_API_KEY` und `BEARBLOG_SUBDOMAIN` bereitstellen. Sie haben Vorrang vor der Konfigurationsdatei. Die globale Option `--config PATH` wählt eine andere Datei. Schlüssel nicht in Prompts, im Shell-Verlauf oder im Repository ablegen.

## Verwendung

In Codex:

```text
$bearblog Liste alle Entwürfe und geplanten Beiträge auf.
$bearblog Erstelle aus ./article.md einen Entwurf mit dem Tag notes.
$bearblog Plane den Entwurf mit dem Titel Hello für den 1. Dezember 2027 um 09:00 Europe/Paris.
```

In Claude Code `$bearblog` durch `/bearblog` ersetzen. Zielinhalt und Änderungen angeben, bei geplanter Veröffentlichung auch die Zeitzone. Suche und Stapelbearbeitung führt der Agent mit aufeinanderfolgenden API-Aufrufen aus.

## Bestandteile

| Bestandteil | Aufgabe |
| --- | --- |
| [SKILL.md](skills/bearblog/SKILL.md) | Agent-Anweisungen und Auswahl der Operationen |
| [scripts/bearblog.py](skills/bearblog/scripts/bearblog.py) | API-Client und CLI ohne externe Laufzeitpakete |
| [scripts/test_bearblog.py](skills/bearblog/scripts/test_bearblog.py) | Offline-Tests mit lokalem HTTP-Server |
| [references/api.md](skills/bearblog/references/api.md) | Endpunkte, Felder, Seitennavigation und Grenzen |
| [references/workflows.md](skills/bearblog/references/workflows.md) | Beispiele für Veröffentlichung, Stapelbearbeitung, Export und Fehlerbehandlung |
| [agents/openai.yaml](skills/bearblog/agents/openai.yaml) | Codex-Anzeigemetadaten |

## Eigenständige CLI

Derselbe Client lässt sich ohne Agenten nutzen. Die Befehle verwenden das zuvor gesetzte `SKILL_DIR`.

```bash
python3 "$SKILL_DIR/scripts/bearblog.py" list-posts --status draft --all
python3 "$SKILL_DIR/scripts/bearblog.py" create-post --data draft.json
python3 "$SKILL_DIR/scripts/bearblog.py" export --output export.json
```

| Befehl | Aktion |
| --- | --- |
| `list-posts --all` | Beiträge auflisten; unterstützt `--status`, `--is-page`, `--page` und `--all` |
| `get-post UID` | Einen Beitrag samt Inhalt abrufen |
| `create-post --data draft.json` | Beitrag erstellen, standardmäßig als Entwurf |
| `update-post UID --data patch.json` | Beitrag bearbeiten, veröffentlichen oder planen |
| `delete-post UID` | Beitrag oder Seite endgültig löschen |
| `get-blog` | Blog-Einstellungen lesen |
| `update-blog --data settings.json` | Nur die übergebenen Einstellungen ändern |
| `export --output export.json` | Einstellungen und alle vollständigen Beiträge exportieren |

Beispiel für `draft.json`:

```json
{"title":"Hello from Bear Blog","content":"A **Markdown** draft.","tags":["notes"]}
```

Bei Änderungen nur die betroffenen Felder übergeben. `--data -` liest JSON von der Standardeingabe. `{"publish":true}` veröffentlicht, `{"publish":false}` setzt auf Entwurf zurück. Geplante Veröffentlichung benötigt `publish:true` und ein zukünftiges `published_date` mit Zeitzone. Alle Felder stehen in der [API-Referenz](skills/bearblog/references/api.md).

## Verhalten und Grenzen

- Deckt alle sieben dokumentierten API-Endpunkte ab. Neue Beiträge sind zunächst Entwürfe; zum Bearbeiten und Löschen die stabile `uid` verwenden.
- Listen enthalten 20 Einträge pro Seite ohne vollständige Inhalte. Der Export ruft jeden Beitrag einzeln ab, enthält keine Mediendateien und ist weder ein konsistenter Schnappschuss noch eine Wiederherstellung mit einem Befehl. Vorhandene Dateien werden nicht überschrieben.
- Der Dienst erlaubt 60 Anfragen pro Minute. Jede Client-Instanz hält Abstände ein und wiederholt 429 höchstens zweimal gemäß `Retry-After`, mit insgesamt maximal 60 Sekunden automatischer Wartezeit. Mehrere Prozesse müssen ihre Gesamtrate abstimmen.
- Schreibvorgänge werden nach Netzwerkfehlern oder 5xx nicht automatisch wiederholt. Zuerst das Ergebnis erneut lesen. Anfragen gehen nur an den offiziellen API-Host; Weiterleitungen werden abgewiesen.
- Die dokumentierte API bietet keine Endpunkte für Medien-Uploads, Statistiken oder Abonnenten. Die lokale Konfiguration liegt im Klartext vor und wird durch Dateirechte geschützt. JSON-Exporte können private Entwürfe enthalten.

## Entwicklung

```bash
python3 -m unittest discover -s skills/bearblog/scripts -p 'test_*.py' -v
```

Tests benötigen keinen API-Schlüssel und greifen nicht auf echte Blogs zu. CLI-Hilfe und Fehlermeldungen sind auf Englisch. Übersetzungskorrekturen und Fehlerberichte sind willkommen.

## Lizenz

[MIT](LICENSE). Ein unabhängiges Projekt ohne Verbindung zu Bear Blog.
