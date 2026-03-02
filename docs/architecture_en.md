# Architecture of the Intelligent JSON Merger

## Overview

The `Intelligent JSON Merger` is designed to provide a flexible and extensible way to combine multiple JSON configurations into a single, cohesive configuration. Its core principle is to allow for hierarchical merging, where later configurations can override or supplement earlier ones, with special handling for complex data types like nested objects and lists. The architecture focuses on modularity, testability, and ease of extension for future intelligent merging capabilities.

## Core Components

### 1. `JsonMerger` Class

This is the primary entry point for the library. It orchestrates the configuration loading and merging process.

-   **`__init__(self)`**: Initializes the merger instance. Currently, it's a lightweight constructor, but it could be extended to accept global merge strategies or custom resolvers.
-   **`merge_configs(self, *configs: Union[str, Dict[str, Any]]) -> Dict[str, Any]`**: This public method accepts a variable number of configuration sources. Each source can be either a file path (string) or an already loaded Python dictionary. It iterates through these sources, loads them if necessary, and applies the merging logic sequentially.
-   **`_deep_merge(self, base: Any, new: Any) -> Any`**: A private helper method that implements the recursive deep merging logic. This is where the "intelligence" of combining different JSON structures resides.

### 2. Merging Strategy (`_deep_merge` logic)

The current `_deep_merge` method implements the following strategy:

-   **Dictionaries (`dict`)**: If both `base` and `new` are dictionaries, they are recursively merged. Keys present in `new` will either overwrite scalar values in `base` or trigger a recursive merge for nested dictionaries. Keys only in `new` are added to `base`.
-   **Lists (`list`)**: If both `base` and `new` are lists, `new` elements are appended to `base`, with a simple deduplication mechanism for primitive types (strings, numbers, booleans) to avoid redundant entries. The order of existing elements in `base` is preserved.
-   **Other Types (Scalars, `None`)**: If types conflict (e.g., merging a `dict` with a `str`) or if both are scalar values, the value from `new` always takes precedence and overwrites the `base` value.

## Data Flow

1.  **Input Configuration Sources**: The `merge_configs` method receives a sequence of configuration sources (file paths or dictionaries).
2.  **Loading**: For each string input, the system attempts to open and parse it as a JSON file. Error handling is in place for `FileNotFoundError` and `json.JSONDecodeError`.
3.  **Sequential Merging**: The configurations are processed in the order they are provided. Each subsequent configuration is merged into the cumulative "final configuration" using the `_deep_merge` logic.
4.  **Output**: The method returns a single, deeply merged Python dictionary representing the final configuration.

```mermaid
graph TD
    A[Start]
    B(Input Config Sources: File Paths or Dictionaries)
    C{Is source a file path?}
    D[Load JSON from file]
    E[Handle FileNotFoundError/JSONDecodeError]
    F[Use dictionary directly]
    G[Initialize final_config = {}]
    H(Loop through each config source)
    I[current_config = loaded/provided config]
    J[final_config = _deep_merge(final_config, current_config)]
    K[End Loop]
    L[Return final_config]

    A --> B
    B --> H
    H --> C
    C -- Yes --> D
    D --> I
    C -- No --> F
    F --> I
    D -- Error --> E
    E --> H (Continue or raise error)
    I --> J
    J --> H
    K --> L
```

## Future Enhancements & "Intelligent" Aspects

While the current implementation provides robust deep merging, the "intelligent" aspect is designed to be expanded:

-   **Custom Merge Strategies**: Allow users to define specific strategies for certain keys or data types (e.g., `REPLACE_LIST`, `MERGE_LIST_BY_ID`, `INCREMENT_NUMBER`). This could be implemented via a `MergeStrategy` enum or a registry of callable functions.
-   **Context-Aware Merging**: Implement logic that understands the semantic meaning of keys. For example, if a key is named `plugins`, a merge might involve loading and combining plugin definitions rather than just appending strings.
-   **Schema Validation**: Integrate with JSON Schema to validate configurations before or after merging, ensuring the resulting configuration adheres to predefined rules.
-   **Conflict Resolution**: Provide more sophisticated conflict resolution mechanisms beyond simple overwrites, such-as interactive prompts or logging of conflicts.
-   **Environment Variables Integration**: Allow placeholders in JSON configurations to be resolved by environment variables.
-   **YAML Support**: Extend the loader to support YAML files, automatically detecting file types.

This architecture lays a solid foundation for these advanced features, providing a clear separation of concerns between loading, merging, and error handling, making the system highly maintainable and extensible.