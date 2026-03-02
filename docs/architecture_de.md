# Architektur des Intelligenten JSON-Mergers

## Überblick

Der `Intelligent JSON Merger` wurde entwickelt, um eine flexible und erweiterbare Methode zum Kombinieren mehrerer JSON-Konfigurationen zu einer einzigen, kohärenten Konfiguration bereitzustellen. Sein Kernprinzip besteht darin, hierarchisches Zusammenführen zu ermöglichen, bei dem spätere Konfigurationen frühere überschreiben oder ergänzen können, mit einer speziellen Behandlung komplexer Datentypen wie verschachtelter Objekte und Listen. Die Architektur konzentriert sich auf Modularität, Testbarkeit und einfache Erweiterbarkeit für zukünftige intelligente Zusammenführungsfunktionen.

## Kernkomponenten

### 1. `JsonMerger` Klasse

Dies ist der primäre Einstiegspunkt für die Bibliothek. Sie orchestriert den Lade- und Zusammenführungsprozess der Konfiguration.

-   **`__init__(self)`**: Initialisiert die Merger-Instanz. Derzeit ist es ein leichter Konstruktor, könnte aber erweitert werden, um globale Zusammenführungsstrategien oder benutzerdefinierte Resolver zu akzeptieren.
-   **`merge_configs(self, *configs: Union[str, Dict[str, Any]]) -> Dict[str, Any]`**: Diese öffentliche Methode akzeptiert eine variable Anzahl von Konfigurationsquellen. Jede Quelle kann entweder ein Dateipfad (String) oder ein bereits geladenes Python-Dictionary sein. Sie iteriert durch diese Quellen, lädt sie bei Bedarf und wendet die Zusammenführungslogik sequenziell an.
-   **`_deep_merge(self, base: Any, new: Any) -> Any`**: Eine private Hilfsmethode, die die rekursive Tiefen-Zusammenführungslogik implementiert. Hier liegt die „Intelligenz“ des Kombinierens verschiedener JSON-Strukturen.

### 2. Zusammenführungsstrategie (Logik von `_deep_merge`)

Die aktuelle Methode `_deep_merge` implementiert die folgende Strategie:

-   **Dictionaries (`dict`)**: Wenn sowohl `base` als auch `new` Dictionaries sind, werden sie rekursiv zusammengeführt. Schlüssel, die in `new` vorhanden sind, überschreiben entweder skalare Werte in `base` oder lösen eine rekursive Zusammenführung für verschachtelte Dictionaries aus. Schlüssel, die nur in `new` vorhanden sind, werden zu `base` hinzugefügt.
-   **Listen (`list`)**: Wenn sowohl `base` als auch `new` Listen sind, werden `new`-Elemente an `base` angehängt, mit einem einfachen Deduplizierungsmechanismus für primitive Typen (Strings, Zahlen, Booleans), um redundante Einträge zu vermeiden. Die Reihenfolge der vorhandenen Elemente in `base` bleibt erhalten.
-   **Andere Typen (Skalare, `None`)**: Wenn Typen kollidieren (z.B. Zusammenführen eines `dict` mit einem `str`) oder wenn beide skalare Werte sind, hat der Wert aus `new` immer Vorrang und überschreibt den `base`-Wert.

## Datenfluss

1.  **Eingabekonfigurationsquellen**: Die Methode `merge_configs` empfängt eine Sequenz von Konfigurationsquellen (Dateipfade oder Dictionaries).
2.  **Laden**: Für jede String-Eingabe versucht das System, diese als JSON-Datei zu öffnen und zu parsen. Eine Fehlerbehandlung ist für `FileNotFoundError` und `json.JSONDecodeError` vorhanden.
3.  **Sequenzielles Zusammenführen**: Die Konfigurationen werden in der Reihenfolge verarbeitet, in der sie bereitgestellt werden. Jede nachfolgende Konfiguration wird mithilfe der `_deep_merge`-Logik in die kumulative „endgültige Konfiguration“ zusammengeführt.
4.  **Ausgabe**: Die Methode gibt ein einzelnes, tief zusammengeführtes Python-Dictionary zurück, das die endgültige Konfiguration darstellt.

```mermaid
graph TD
    A[Start]
    B(Eingabekonfigurationsquellen: Dateipfade oder Dictionaries)
    C{Ist die Quelle ein Dateipfad?}
    D[Lade JSON aus Datei]
    E[Behandle FileNotFoundError/JSONDecodeError]
    F[Verwende Dictionary direkt]
    G[Initialisiere final_config = {}]
    H(Schleife durch jede Konfigurationsquelle)
    I[current_config = geladene/bereitgestellte Konfiguration]
    J[final_config = _deep_merge(final_config, current_config)]
    K[Schleifenende]
    L[Gib final_config zurück]

    A --> B
    B --> H
    H --> C
    C -- Ja --> D
    D --> I
    C -- Nein --> F
    F --> I
    D -- Fehler --> E
    E --> H (Fortsetzen oder Fehler auslösen)
    I --> J
    J --> H
    K --> L
```

## Zukünftige Verbesserungen & „Intelligente“ Aspekte

Während die aktuelle Implementierung ein robustes tiefes Zusammenführen bietet, ist der „intelligente“ Aspekt so konzipiert, dass er erweitert werden kann:

-   **Benutzerdefinierte Zusammenführungsstrategien**: Ermöglichen Sie Benutzern, spezifische Strategien für bestimmte Schlüssel oder Datentypen zu definieren (z.B. `REPLACE_LIST`, `MERGE_LIST_BY_ID`, `INCREMENT_NUMBER`). Dies könnte über ein `MergeStrategy`-Enum oder ein Register von aufrufbaren Funktionen implementiert werden.
-   **Kontextsensitives Zusammenführen**: Implementieren Sie Logik, die die semantische Bedeutung von Schlüsseln versteht. Wenn beispielsweise ein Schlüssel `plugins` heißt, könnte ein Zusammenführen das Laden und Kombinieren von Plugin-Definitionen umfassen, anstatt nur Strings anzuhängen.
-   **Schema-Validierung**: Integration mit JSON Schema zur Validierung von Konfigurationen vor oder nach dem Zusammenführen, um sicherzustellen, dass die resultierende Konfiguration vordefinierten Regeln entspricht.
-   **Konfliktlösung**: Bieten Sie ausgefeiltere Konfliktlösungsmechanismen über einfache Überschreibungen hinaus, wie z.B. interaktive Eingabeaufforderungen oder die Protokollierung von Konflikten.
-   **Umgebungsvariablen-Integration**: Ermöglichen Sie die Auflösung von Platzhaltern in JSON-Konfigurationen durch Umgebungsvariablen.
-   **YAML-Unterstützung**: Erweitern Sie den Loader, um YAML-Dateien zu unterstützen und Dateitypen automatisch zu erkennen.

Diese Architektur legt ein solides Fundament für diese erweiterten Funktionen und bietet eine klare Trennung der Belange zwischen Laden, Zusammenführen und Fehlerbehandlung, wodurch das System hochgradig wartbar und erweiterbar wird.