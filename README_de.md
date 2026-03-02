# Intelligenter JSON-Merger

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI/CD](https://github.com/your-org/intelligent-json-merger/actions/workflows/python-app.yml/badge.svg)](https://github.com/your-org/intelligent-json-merger/actions/workflows/python-app.yml)

## 💡 Über das Projekt

`Intelligent JSON Merger` ist eine robuste, unternehmensfähige und quelloffene Python-Bibliothek, die entwickelt wurde, um JSON-Konfigurationsdateien und Dictionaries intelligent zusammenzuführen. Sie bietet eine flexible und leistungsstarke Möglichkeit, Anwendungseinstellungen zu verwalten, indem sie hierarchische Überschreibungen, tiefes Zusammenführen von Objekten und eine intelligente Behandlung von Listen ermöglicht, um sicherzustellen, dass Ihre Konfigurationen immer konsistent und vorhersehbar sind.

Dieses Projekt zielt darauf ab, das häufige Problem der Verwaltung komplexer Konfigurationen in verschiedenen Umgebungen (Entwicklung, Staging, Produktion) oder für modulare Anwendungen zu lösen, bei denen Einstellungen an mehreren Stellen definiert sind. Es geht über einfache Überschreibungen hinaus, indem es die Struktur von JSON-Daten versteht und kontextsensitive Zusammenführungsstrategien anwendet.

## ✨ Funktionen

-   **Tiefes Zusammenführen (Deep Merging)**: Führt verschachtelte JSON-Objekte rekursiv zusammen.
-   **Listenbehandlung**: Fügt Listen standardmäßig eindeutige Elemente hinzu und vermeidet Duplikate.
-   **Flexible Eingabe**: Zusammenführen aus Dateipfaden oder direkt aus Python-Dictionaries.
-   **Hierarchische Überschreibungen**: Spätere Konfigurationen haben Vorrang vor früheren.
-   **Fehlerbehandlung**: Robuste Fehlerberichterstattung für ungültige Dateipfade oder fehlerhaftes JSON.
-   **Erweiterbares Design**: Modulare Architektur, die zukünftige benutzerdefinierte Zusammenführungsstrategien ermöglicht.
-   **Typ-Hinweise (Type Hinting)**: Vollständig mit Typ-Hinweisen versehen für bessere Codequalität und Wartbarkeit.

## 🚀 Installation

```bash
git clone https://github.com/your-org/intelligent-json-merger.git
cd intelligent-json-merger
pip install -r requirements.txt
```

## 📖 Verwendung

### Grundlegendes Zusammenführen

Um mehrere JSON-Dateien oder Dictionaries zusammenzuführen, übergeben Sie diese einfach der Methode `merge_configs`:

Erstellen Sie `config_base.json`:

```json
{
  "app_name": "MyWebApp",
  "version": "1.0.0",
  "settings": {
    "debug": true,
    "port": 8080,
    "features": ["auth", "logging"]
  },
  "database": {
    "host": "localhost"
  }
}
```

Erstellen Sie `config_env_dev.json`:

```json
{
  "version": "1.0.1-dev",
  "settings": {
    "debug": true,
    "port": 9000,
    "features": ["dev-tools", "auth"]
  },
  "database": {
    "user": "dev_user",
    "password": "dev_pass"
  }
}
```

Führen Sie sie nun zusammen:

```python
from main import JsonMerger
import json

merger = JsonMerger()

merged_config = merger.merge_configs(
    "config_base.json",
    "config_env_dev.json",
    {
        "settings": {
            "debug": True, # Erneut überschreiben
            "log_level": "DEBUG"
        }
    }
)

print(json.dumps(merged_config, indent=4))
```

Ausgabe:

```json
{
    "app_name": "MyWebApp",
    "version": "1.0.1-dev",
    "settings": {
        "debug": true,
        "port": 9000,
        "features": [
            "auth",
            "logging",
            "dev-tools"
        ],
        "log_level": "DEBUG"
    },
    "database": {
        "host": "localhost",
        "user": "dev_user",
        "password": "dev_pass"
    }
}
```

### Fehlerbehandlung

Die Methode `merge_configs` löst `ValueError` für dateibezogene Probleme oder ungültiges JSON und `TypeError` für falsche Eingabetypen aus.

```python
try:
    merger.merge_configs("nicht_existierende_datei.json")
except ValueError as e:
    print(f"Fehler: {e}")

try:
    merger.merge_configs({"gültig": true}, "{"ungültig": "json"}") # Fehlerhafter String
except ValueError as e:
    print(f"Fehler: {e}")
```

## 🤝 Mitwirken

Wir freuen uns über Beiträge! Details zum Einstieg finden Sie in unserer [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – weitere Details finden Sie in der Datei [LICENSE](LICENSE).