# Automated Database Normalization Checker

A Python tool to detect and report normalization violations up to 3NF in a live PostgreSQL database or from schema/FD JSON fixtures. Combines schema extraction, user-provided functional dependencies (FDs), and algorithmic analysis to produce 2NF/3NF decompositions.

![DB Normalizer](/assets/DB_Normalizer.png)

## Motivation

-   Database normalization is typically taught as a theoretical exercise, while real-world schemas are live, evolving, and often lack explicitly documented functional dependencies.
-   Existing tools rarely bridge formal normalization theory with practical database inspection and refactoring.
-   This project explores how classical normalization algorithms (2NF/3NF) can be applied to real PostgreSQL schemas using user-supplied functional dependencies.
-   The goal is to make normalization analysis repeatable, inspectable, and developer-friendly through a simple CLI workflow.

## Features

-   Extracts schema metadata from PostgreSQL using SQLAlchemy.
-   Parses Functional Dependencies from JSON files.
-   Computes candidate keys.
-   Detects 1NF/2NF/3NF violations and performs decomposition (2NF/3NF).
-   CLI for running analysis and exporting results (JSON/text).

## Quick start

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

4. Or extract schema from DB (requires a .env file):

    Create a `.env` file in the project root with the following variables:

    ```
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=myuser
    DB_PASSWORD=supersecret
    ```

    Then, run analyzer with database name

    ```
    python -m db_normalizer --database "dbname" --dependencies path\to\fds.json --level 3NF
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
-   --out_prefix Output filename (default: decomposed.json)

Example:

```
python -m db_normalizer --schema-file schema1.json --dependencies fds1.json --level 3NF --out_prefix result
```

## Notes

-   The tool expects FDs in a JSON mapping where composite LHS keys are comma-separated strings.
-   2NF decomposition preserves ability to join back via original keys; 3NF decomposition removes transitive dependencies.

## Discussion & Limitations

-   The implementation takes a pragmatic approach by relying on declared primary keys and user-supplied functional dependencies to drive normalization and decomposition.
-   This design simplifies the normalization engine and works well for many real-world schemas, especially when documentation of constraints is incomplete.
-   However, the current approach may miss cases involving alternate candidate keys or incomplete functional dependency sets, which can affect correct identification of prime attributes.
-   As a result, some edge cases in 2NF/3NF analysis may not be fully captured under complex dependency structures.

## Future Work

-   Implement attribute-closure and minimal-cover computation to improve dependency analysis.
-   Enumerate minimal candidate keys rather than relying solely on declared primary keys.
-   Explore optional data-driven functional dependency discovery from instance data.

License: MIT (see LICENSE file).

<footer style="text-align: center">© 2025 Sujan Maharjan</footer>
