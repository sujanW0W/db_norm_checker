# Automated Database Normalization Checker

A Python tool to detect and report normalization violations up to 3NF in a live PostgreSQL database or from schema/FD JSON fixtures. Combines schema extraction, user-provided functional dependencies (FDs), and algorithmic analysis to produce 2NF/3NF decompositions.

## Features

-   Extracts schema metadata from PostgreSQL using SQLAlchemy.
-   Parses Functional Dependencies from JSON files.
-   Computes candidate keys.
-   Detects 1NF/2NF/3NF violations and performs decomposition (2NF/3NF).
-   CLI for running analysis and exporting results (JSON/text).

## Quick start (Windows)

1. Create and activate a virtual environment:

    ```
    python -m venv venv
    venv\Scripts\activate
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    # or if using pyproject.toml: pip install -e .
    ```

3. Run analyzer with schema file:

    ```
    python -m db_normalizer --schema-file path\to\schema.json --dependencies path\to\fds.json --level 2NF
    ```

4. Or extract schema from DB (DSN/connection string):
    ```
    python -m db_normalizer --dsn "postgresql://user:pass@host:5432/dbname" --dependencies path\to\fds.json --level 3NF
    ```

## Project layout

-   DB_Project/
    -   pyproject.toml
    -   requirements.txt
    -   README.md
    -   LICENSE
    -   .gitignore
    -   run.sh
    -   src/
        -   db_normalizer/
            -   **init**.py
            -   **main**.py
            -   algorithm.py
            -   cli.py
            -   connection.py
            -   extract_schema.py
            -   read_json.py
    -   tests/
        -   fixtures/
            -   test_schema.json
            -   test_dependencies.json
    -   docs/

## CLI

Options:

-   --database PostgreSQL (overrides --schema-file)
-   --schema Path to schema JSON
-   --dependencies Path to FD JSON (required)
-   --level 2NF or 3NF (default: 2NF)
-   --out_prefix Output filename (default: {level}.json)

Example:

```
python -m db_normalizer --schema-file schema1.json --dependencies fds1.json --level 3NF --out result.json
```

## Notes

-   The tool expects FDs in a JSON mapping where composite LHS keys are comma-separated strings.
-   2NF decomposition preserves ability to join back via original keys; 3NF decomposition removes transitive dependencies.

License: MIT (see LICENSE file).

<footer style="text-align: center">© 2025 Sujan Maharjan</footer>
