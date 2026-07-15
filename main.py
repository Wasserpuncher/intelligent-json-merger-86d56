import argparse
import json
import os
import sys
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
            merged_list = list(base) # Erstelle eine Kopie der Basislise, um die Originalreferenz nicht zu ändern.
                                     # Create a copy of the base list to avoid modifying the original reference.
            for item in new:
                if item not in merged_list: # Einfache Deduplizierung für primitive Typen in Listen.
                                            # Simple deduplication for primitive types in lists.
                    merged_list.append(item)
            return merged_list
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


# Standardname der Merge-Steuerungsdatei, falls kein Pfad angegeben wird.
# Default name of the merge control file if no path is provided.
DEFAULT_MERGE_CONFIG_FILENAME = "merge-config.json"


class MergeRunConfig:
    """
    Beschreibt einen kompletten Merge-Lauf, geladen aus einer JSON-Steuerungsdatei.
    Die Steuerungsdatei benennt die zu ladenden Eingabedateien und das Ausgabeziel,
    sodass mehrere JSON-Dateien ohne Code-Änderungen gemergt werden können.

    Describes a complete merge run loaded from a JSON control file.
    The control file names the input files to load and the output target, so
    multiple JSON files can be merged without code changes.
    """

    def __init__(self, inputs: List[str], output: Optional[str] = None) -> None:
        """
        Args:
            inputs: Geordnete Liste der zu mergenden JSON-Eingabedateien.
                    Ordered list of JSON input files to merge.
            output: Optionaler Pfad, in den das Ergebnis geschrieben wird.
                    Optional path the result is written to.
        """
        self.inputs = inputs
        self.output = output

    @staticmethod
    def from_dict(data: Any) -> "MergeRunConfig":
        """
        Erzeugt eine MergeRunConfig aus einem geparsten JSON-Objekt und validiert die Felder.
        Creates a MergeRunConfig from a parsed JSON object and validates the fields.

        Raises:
            ValueError: Wenn Pflichtfelder fehlen oder Werte ungültig sind.
                        If required fields are missing or values are invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Die Merge-Steuerungsdatei muss ein JSON-Objekt sein.")

        raw_inputs = data.get("inputs")
        if not isinstance(raw_inputs, list) or not raw_inputs:
            raise ValueError("Die Steuerungsdatei benötigt ein nicht-leeres 'inputs'-Array.")
        inputs: List[str] = []
        for item in raw_inputs:
            if not isinstance(item, str):
                raise ValueError("Jeder Eintrag in 'inputs' muss ein Dateipfad (String) sein.")
            inputs.append(item)

        output = data.get("output")
        if output is not None and not isinstance(output, str):
            raise ValueError("'output' muss ein Dateipfad (String) oder null sein.")

        return MergeRunConfig(inputs=inputs, output=output)


def load_run_config(config_path: str = DEFAULT_MERGE_CONFIG_FILENAME) -> MergeRunConfig:
    """
    Lädt und validiert eine Merge-Steuerungsdatei von der Festplatte.
    Loads and validates a merge control file from disk.

    Raises:
        FileNotFoundError: Wenn die Steuerungsdatei fehlt. If the control file is missing.
        json.JSONDecodeError: Wenn die Datei kein gültiges JSON ist. If it is not valid JSON.
        ValueError: Wenn der Inhalt kein gültiges Merge-Schema beschreibt. If schema is invalid.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Merge-Steuerungsdatei nicht gefunden: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MergeRunConfig.from_dict(data)


def run_from_config(config_path: str = DEFAULT_MERGE_CONFIG_FILENAME) -> Dict[str, Any]:
    """
    Führt einen kompletten Merge anhand einer Steuerungsdatei aus: lädt alle
    benannten Eingabedateien, mergt sie in Reihenfolge und schreibt das Ergebnis
    -- falls angegeben -- in die Ausgabedatei. Gibt die zusammengeführte Struktur zurück.

    Runs a complete merge driven by a control file: loads all named input files,
    merges them in order and -- if requested -- writes the result to the output
    file. Returns the merged structure.
    """
    run_config = load_run_config(config_path)
    merger = JsonMerger()
    # Die Eingabedateipfade werden direkt an merge_configs übergeben, das jede
    # Datei lädt und tiefgehend zusammenführt.
    # The input file paths are passed straight to merge_configs, which loads and
    # deep-merges each file.
    sources: List[Union[str, Dict[str, Any]]] = list(run_config.inputs)
    result = merger.merge_configs(*sources)
    if run_config.output is not None:
        with open(run_config.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    """
    Kommandozeilen-Einstiegspunkt: steuert einen Merge über eine JSON-Steuerungsdatei.
    Command line entry point: drives a merge via a JSON control file.
    """
    parser = argparse.ArgumentParser(
        description="Merge multiple JSON files driven by a JSON control file.",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_MERGE_CONFIG_FILENAME,
        help=f"Path to the merge control file (default: {DEFAULT_MERGE_CONFIG_FILENAME}).",
    )
    args = parser.parse_args(argv)
    try:
        result = run_from_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=4, ensure_ascii=False))
    return 0


def _run_demo() -> None:
    # Beispielnutzung des JsonMergers
    # Example usage of the JsonMerger
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
    os.remove("config1.json")
    os.remove("config2.json")
    os.remove("config3.json")
    print("\n--- Temporäre Konfigurationsdateien entfernt ---")


if __name__ == "__main__":
    sys.exit(main())