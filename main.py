import json
from typing import Any, Dict, List, Union, Optional

class JsonMerger:
    """
    Ein intelligenter JSON-Konfigurationsmerger zur konsistenten Verwaltung von Anwendungseinstellungen.
    This intelligent JSON configuration merger consistently manages application settings.
    """

    def __init__(self):
        """
        Initialisiert den JsonMerger.
        Initializes the JsonMerger.
        """
        pass

    def _deep_merge(self, base: Any, new: Any) -> Any:
        """
        Führt zwei beliebige JSON-Strukturen tiefgehend zusammen.
        Behandelt Dictionaries durch rekursives Zusammenführen und Listen durch Anhängen neuer Elemente,
        es sei denn, ein Element existiert bereits (einfache Deduplizierung für primitive Typen).
        Deep merges two arbitrary JSON structures.
        Handles dictionaries by recursively merging and lists by appending new elements,
        unless an element already exists (simple deduplication for primitive types).

        Args:
            base (Any): Die Basis-JSON-Struktur.
                        The base JSON structure.
            new (Any): Die neue JSON-Struktur, die in die Basis integriert werden soll.
                       The new JSON structure to integrate into the base.

        Returns:
            Any: Die zusammengeführte JSON-Struktur.
                 The merged JSON structure.
        """
        if isinstance(base, dict) and isinstance(new, dict):
            # Wenn beide Dictionaries sind, führe sie rekursiv zusammen.
            # If both are dictionaries, merge them recursively.
            merged = base.copy()
            for key, value in new.items():
                if key in merged:
                    merged[key] = self._deep_merge(merged[key], value)
                else:
                    merged[key] = value
            return merged
        elif isinstance(base, list) and isinstance(new, list):
            # Wenn beide Listen sind, hänge neue Elemente an, vermeide Duplikate.
            # If both are lists, append new elements, avoiding duplicates.
            merged = list(base) # Erstelle eine Kopie der Basislise, um die Originalreferenz nicht zu ändern.
                                # Create a copy of the base list to avoid modifying the original reference.
            for item in new:
                if item not in merged: # Einfache Deduplizierung für primitive Typen in Listen.
                                       # Simple deduplication for primitive types in lists.
                    merged.append(item)
            return merged
        else:
            # Für alle anderen Typen (Skalare, None, oder Typenkonflikte), überschreibe mit dem neuen Wert.
            # For all other types (scalars, None, or type conflicts), overwrite with the new value.
            return new

    def merge_configs(self, *configs: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Führt eine Liste von JSON-Konfigurationen zusammen.
        Die Konfigurationen können als Dateipfade (Strings) oder als bereits geladene Dictionaries übergeben werden.
        Spätere Konfigurationen überschreiben oder ergänzen frühere.

        Merges a list of JSON configurations.
        Configurations can be passed as file paths (strings) or as already loaded dictionaries.
        Later configurations overwrite or supplement earlier ones.

        Args:
            *configs (Union[str, Dict[str, Any]]): Eine variable Anzahl von Konfigurationen.
                                                    Jede kann ein Dateipfad oder ein Diktat sein.
                                                    A variable number of configurations.

        Returns:
            Dict[str, Any]: Das endgültig zusammengeführte Konfigurationsdiktat.
                            The final merged configuration dictionary.

        Raises:
            ValueError: Wenn eine angegebene Datei nicht gefunden wird oder ungültiges JSON enthält.
                        If a specified file is not found or contains invalid JSON.
        """
        final_config: Dict[str, Any] = {} # Initialisiere das finale Konfigurationsdiktat.
                                         # Initialize the final configuration dictionary.

        for config_source in configs:
            current_config: Dict[str, Any]

            if isinstance(config_source, str):
                # Wenn der Quellcode ein String ist, versuche ihn als Dateipfad zu laden.
                # If the source is a string, try to load it as a file path.
                try:
                    with open(config_source, 'r', encoding='utf-8') as f:
                        current_config = json.load(f) # Lade JSON aus der Datei.
                                                      # Load JSON from the file.
                except FileNotFoundError:
                    # Dateifehler behandeln.
                    # Handle file not found error.
                    raise ValueError(f"Konfigurationsdatei nicht gefunden: '{config_source}'")
                except json.JSONDecodeError as e:
                    # JSON-Dekodierungsfehler behandeln.
                    # Handle JSON decode error.
                    raise ValueError(f"Ungültiges JSON in Datei '{config_source}': {e}")
                except Exception as e:
                    # Alle anderen Dateizugriffsfehler abfangen.
                    # Catch all other file access errors.
                    raise ValueError(f"Fehler beim Laden der Datei '{config_source}': {e}")
            elif isinstance(config_source, dict):
                # Wenn der Quellcode bereits ein Diktat ist, verwende ihn direkt.
                # If the source is already a dictionary, use it directly.
                current_config = config_source
            else:
                # Ungültigen Konfigurationstyp behandeln.
                # Handle invalid configuration type.
                raise TypeError(f"Ungültiger Konfigurationstyp: {type(config_source)}. Erwartet wird str (Dateipfad) oder dict.")

            # Führe die aktuelle Konfiguration tiefgehend mit der finalen Konfiguration zusammen.
            # Deep merge the current configuration with the final configuration.
            final_config = self._deep_merge(final_config, current_config)

        return final_config

# Beispielnutzung des JsonMergers
# Example usage of the JsonMerger
if __name__ == "__main__":
    merger = JsonMerger()

    # Erstelle einige temporäre Konfigurationsdateien für das Beispiel
    # Create some temporary configuration files for the example
    config1_data = {
        "app_name": "MyAwesomeApp",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "port": 8080,
            "features": ["auth", "logging"]
        },
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }

    config2_data = {
        "version": "1.0.1",
        "settings": {
            "port": 9000,
            "features": ["analytics", "auth"]
        },
        "database": {
            "user": "admin"
        },
        "new_feature": {
            "enabled": True
        }
    }

    config3_data = {
        "settings": {
            "debug": False,
            "timeout": 30
        },
        "database": {
            "host": "production.db.com"
        },
        "features": ["caching"] # Dies wird nicht direkt gemerged, da es auf oberster Ebene ist.
                               # This will not be merged directly as it is at the top level.
    }

    # Speichere die Konfigurationen in temporären Dateien
    # Save the configurations to temporary files
    with open("config1.json", "w", encoding='utf-8') as f:
        json.dump(config1_data, f, indent=4)
    with open("config2.json", "w", encoding='utf-8') as f:
        json.dump(config2_data, f, indent=4)
    with open("config3.json", "w", encoding='utf-8') as f:
        json.dump(config3_data, f, indent=4)

    print("--- Konfigurationen zusammenführen ---")
    # Merge configurations from files and a dictionary
    try:
        merged_config = merger.merge_configs(
            "config1.json",
            config2_data, # Kann auch als Diktat übergeben werden
                          # Can also be passed as a dictionary
            "config3.json"
        )
        print("Zusammengeführte Konfiguration:")
        # Print the merged configuration
        print(json.dumps(merged_config, indent=4))

        # Erwartetes Ergebnis (Anmerkungen):
        # - app_name: "MyAwesomeApp" (von config1)
        # - version: "1.0.1" (config2 überschreibt config1)
        # - settings.debug: False (config3 überschreibt config1)
        # - settings.port: 9000 (config2 überschreibt config1)
        # - settings.timeout: 30 (von config3)
        # - settings.features: ["auth", "logging", "analytics"] (Listen werden zusammengeführt, Duplikate entfernt)
        # - database.host: "production.db.com" (config3 überschreibt config1)
        # - database.port: 5432 (von config1)
        # - database.user: "admin" (von config2)
        # - new_feature.enabled: True (von config2)

    except (ValueError, TypeError) as e:
        print(f"Fehler beim Zusammenführen der Konfigurationen: {e}")

    # Aufräumen der temporären Dateien
    # Clean up temporary files
    import os
    os.remove("config1.json")
    os.remove("config2.json")
    os.remove("config3.json")
    print("\n--- Temporäre Konfigurationsdateien entfernt ---")