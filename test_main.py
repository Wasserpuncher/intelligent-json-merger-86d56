import unittest
import json
import os
import tempfile
import shutil
from typing import Any
from main import (
    JsonMerger,
    MergeRunConfig,
    load_run_config,
    run_from_config,
    main,
)

class TestJsonMerger(unittest.TestCase):
    """
    Testfälle für die JsonMerger-Klasse.
    Test cases for the JsonMerger class.
    """

    def setUp(self):
        """
        Setzt den Test auf, indem eine Instanz des Mergers erstellt wird und temporäre Dateien vorbereitet werden.
        Sets up the test by creating a merger instance and preparing temporary files.
        """
        self.merger = JsonMerger()
        # Temporäre Konfigurationsdateien für Tests erstellen.
        # Create temporary configuration files for tests.
        self.temp_config1 = "test_config1.json"
        self.temp_config2 = "test_config2.json"
        self.temp_config_invalid = "test_config_invalid.json"

        self.config1_data = {
            "app_name": "TestApp",
            "version": "1.0",
            "settings": {
                "debug": True,
                "port": 8080,
                "features": ["featureA", "featureB"]
            },
            "database": {
                "host": "localhost"
            }
        }

        self.config2_data = {
            "version": "1.1",
            "settings": {
                "port": 9000,
                "timeout": 30,
                "features": ["featureB", "featureC"]
            },
            "database": {
                "user": "testuser"
            },
            "new_key": "value"
        }

        with open(self.temp_config1, 'w', encoding='utf-8') as f:
            json.dump(self.config1_data, f, indent=4)
        with open(self.temp_config2, 'w', encoding='utf-8') as f:
            json.dump(self.config2_data, f, indent=4)
        with open(self.temp_config_invalid, 'w', encoding='utf-8') as f:
            f.write("{'invalid_json': true}") # Ungültiges JSON-Format

    def tearDown(self):
        """
        Räumt nach jedem Test auf, indem temporäre Dateien gelöscht werden.
        Cleans up after each test by deleting temporary files.
        """
        if os.path.exists(self.temp_config1):
            os.remove(self.temp_config1)
        if os.path.exists(self.temp_config2):
            os.remove(self.temp_config2)
        if os.path.exists(self.temp_config_invalid):
            os.remove(self.temp_config_invalid)

    def test_basic_merge(self):
        """
        Testet das grundlegende Zusammenführen zweier Dictionaries.
        Tests the basic merging of two dictionaries.
        """
        merged = self.merger.merge_configs(self.config1_data, self.config2_data)
        expected = {
            "app_name": "TestApp",
            "version": "1.1",
            "settings": {
                "debug": True,
                "port": 9000,
                "features": ["featureA", "featureB", "featureC"],
                "timeout": 30
            },
            "database": {
                "host": "localhost",
                "user": "testuser"
            },
            "new_key": "value"
        }
        self.assertEqual(merged, expected)

    def test_merge_from_files(self):
        """
        Testet das Zusammenführen von Konfigurationen aus Dateien.
        Tests merging configurations from files.
        """
        merged = self.merger.merge_configs(self.temp_config1, self.temp_config2)
        expected = {
            "app_name": "TestApp",
            "version": "1.1",
            "settings": {
                "debug": True,
                "port": 9000,
                "features": ["featureA", "featureB", "featureC"],
                "timeout": 30
            },
            "database": {
                "host": "localhost",
                "user": "testuser"
            },
            "new_key": "value"
        }
        self.assertEqual(merged, expected)

    def test_single_config(self):
        """
        Testet das Laden einer einzelnen Konfiguration.
        Tests loading a single configuration.
        """
        merged = self.merger.merge_configs(self.config1_data)
        self.assertEqual(merged, self.config1_data)

        merged_from_file = self.merger.merge_configs(self.temp_config1)
        self.assertEqual(merged_from_file, self.config1_data)

    def test_empty_configs(self):
        """
        Testet das Zusammenführen ohne Konfigurationen.
        Tests merging with no configurations.
        """
        merged = self.merger.merge_configs()
        self.assertEqual(merged, {})

    def test_non_existent_file(self):
        """
        Testet den Fehlerfall, wenn eine Datei nicht existiert.
        Tests the error case when a file does not exist.
        """
        with self.assertRaisesRegex(ValueError, "Konfigurationsdatei nicht gefunden"): # Erwartet einen ValueError
                                                                                 # Expects a ValueError
            self.merger.merge_configs("non_existent.json")

    def test_invalid_json_file(self):
        """
        Testet den Fehlerfall bei einer ungültigen JSON-Datei.
        Tests the error case with an invalid JSON file.
        """
        with self.assertRaisesRegex(ValueError, "Ungültiges JSON in Datei"): # Erwartet einen ValueError
                                                                          # Expects a ValueError
            self.merger.merge_configs(self.temp_config_invalid)

    def test_type_mismatch_overwrite(self):
        """
        Testet das Überschreiben bei Typenkonflikten (z.B. String statt Dict).
        Tests overwriting on type mismatches (e.g., string instead of dict).
        """
        config_base = {"key": {"nested": 1}}
        config_new = {"key": "string_value"}
        merged = self.merger.merge_configs(config_base, config_new)
        self.assertEqual(merged, {"key": "string_value"})

        config_base_list = {"key": [1, 2]}
        config_new_scalar = {"key": 3}
        merged_scalar = self.merger.merge_configs(config_base_list, config_new_scalar)
        self.assertEqual(merged_scalar, {"key": 3})

    def test_list_merging(self):
        """
        Testet das Zusammenführen von Listen mit Duplikaten und neuen Elementen.
        Tests merging lists with duplicates and new elements.
        """
        config_base = {"list_key": [1, 2, "a"]}
        config_new = {"list_key": ["a", 3, "b"]}
        merged = self.merger.merge_configs(config_base, config_new)
        # Die Reihenfolge der Elemente kann variieren, daher prüfen wir auf Satzgleichheit.
        # The order of elements might vary, so we check for set equality (after converting to set).
        self.assertIsInstance(merged['list_key'], list)
        self.assertEqual(set(merged['list_key']), {1, 2, "a", 3, "b"})

    def test_nested_empty_dicts_and_lists(self):
        """
        Testet das Zusammenführen mit leeren verschachtelten Dictionaries und Listen.
        Tests merging with empty nested dictionaries and lists.
        """
        config_base = {"a": {"b": {}}, "c": []}
        config_new = {"a": {"d": 1}, "c": [1, 2]}
        merged = self.merger.merge_configs(config_base, config_new)
        expected = {"a": {"b": {}, "d": 1}, "c": [1, 2]}
        self.assertEqual(merged, expected)

    def test_multiple_configs_order(self):
        """
        Testet die Reihenfolge der Zusammenführung bei mehreren Konfigurationen.
        Spätere Konfigurationen sollten frühere Werte überschreiben.
        Tests the order of merging with multiple configurations.
        Later configurations should overwrite earlier values.
        """
        config_a = {"key": 1, "nested": {"x": 10}}
        config_b = {"key": 2, "nested": {"y": 20}}
        config_c = {"key": 3, "nested": {"x": 30, "z": 30}}

        merged = self.merger.merge_configs(config_a, config_b, config_c)
        expected = {"key": 3, "nested": {"x": 30, "y": 20, "z": 30}}
        self.assertEqual(merged, expected)

class TestMergeRunConfig(unittest.TestCase):
    """
    Tests für den steuerungsdatei-gesteuerten Merge mehrerer JSON-Dateien (Issue #1).
    Tests for the control-file-driven merge of multiple JSON files (Issue #1).
    """

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_json(self, name: str, data: Any) -> str:
        path = os.path.join(self.tmpdir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_from_dict_valid(self) -> None:
        cfg = MergeRunConfig.from_dict(
            {"inputs": ["a.json", "b.json"], "output": "out.json"}
        )
        self.assertEqual(cfg.inputs, ["a.json", "b.json"])
        self.assertEqual(cfg.output, "out.json")

    def test_from_dict_defaults_output_none(self) -> None:
        cfg = MergeRunConfig.from_dict({"inputs": ["a.json"]})
        self.assertIsNone(cfg.output)

    def test_from_dict_missing_inputs(self) -> None:
        with self.assertRaises(ValueError):
            MergeRunConfig.from_dict({"output": "out.json"})

    def test_from_dict_non_string_input(self) -> None:
        with self.assertRaises(ValueError):
            MergeRunConfig.from_dict({"inputs": [123]})

    def test_load_run_config_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_run_config(os.path.join(self.tmpdir, "missing.json"))

    def test_run_from_config_merges_multiple_files_to_output(self) -> None:
        # Drei echte Eingabedateien schreiben und über die Steuerungsdatei mergen.
        # Write three real input files and merge them through the control file.
        self._write_json(
            "c1.json",
            {"app": "demo", "settings": {"debug": True, "features": ["auth"]}},
        )
        self._write_json(
            "c2.json",
            {"version": "1.1", "settings": {"features": ["metrics"]}},
        )
        self._write_json(
            "c3.json",
            {"settings": {"debug": False}},
        )
        output_path = os.path.join(self.tmpdir, "merged.json")
        config_path = self._write_json(
            "merge-config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "c1.json"),
                    os.path.join(self.tmpdir, "c2.json"),
                    os.path.join(self.tmpdir, "c3.json"),
                ],
                "output": output_path,
            },
        )
        result = run_from_config(config_path)
        expected = {
            "app": "demo",
            "settings": {"debug": False, "features": ["auth", "metrics"]},
            "version": "1.1",
        }
        self.assertEqual(result, expected)
        # Die Ausgabedatei muss wirklich geschrieben worden sein.
        # The output file must actually have been written.
        with open(output_path, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f), expected)

    def test_run_from_config_without_output_returns_result(self) -> None:
        self._write_json("a.json", {"x": 1})
        self._write_json("b.json", {"y": 2})
        config_path = self._write_json(
            "merge-config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "a.json"),
                    os.path.join(self.tmpdir, "b.json"),
                ]
            },
        )
        result = run_from_config(config_path)
        self.assertEqual(result, {"x": 1, "y": 2})

    def test_run_from_config_invalid_input_file(self) -> None:
        # Eine Eingabedatei mit ungültigem JSON muss als ValueError gemeldet werden.
        # An input file with invalid JSON must be surfaced as a ValueError.
        bad_path = os.path.join(self.tmpdir, "bad.json")
        with open(bad_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        config_path = self._write_json(
            "merge-config.json", {"inputs": [bad_path]}
        )
        with self.assertRaises(ValueError):
            run_from_config(config_path)

    def test_main_cli_success(self) -> None:
        self._write_json("a.json", {"x": 1})
        self._write_json("b.json", {"y": 2})
        config_path = self._write_json(
            "merge-config.json",
            {
                "inputs": [
                    os.path.join(self.tmpdir, "a.json"),
                    os.path.join(self.tmpdir, "b.json"),
                ]
            },
        )
        self.assertEqual(main(["--config", config_path]), 0)

    def test_main_cli_missing_config(self) -> None:
        self.assertEqual(main(["--config", os.path.join(self.tmpdir, "nope.json")]), 1)


if __name__ == '__main__':
    unittest.main()