"""normalizer.py

Script for creating a pipleine to connect database, extract FDs, and normalize to normal forms.

Usage example:
python normalizer.py --database my_database --dependencies dependencies.json --level 3NF --out_prefix relation_3NF

"""

import sys
import json
import traceback
from argparse import ArgumentParser

from read_json import extract_json
from extract_schema import get_schema
from algorithm import extract_keys, get_full_partial_transitive_fd, decompose_to_2NF, decomponse_to_3NF


def pipeline(schema: dict, dependencies: dict, normalization_level: str, out_prefix: str = "final"):
    keys = extract_keys(schema)

    dependencies_dict = get_full_partial_transitive_fd(dependencies, keys)

    relation_2NF, dependencies_dict = decompose_to_2NF(
        schema, keys, dependencies_dict)

    if normalization_level == "3NF":
        relation = decomponse_to_3NF(relation_2NF, dependencies_dict)
    else:
        relation = relation_2NF

    out_file = f"{out_prefix}.json"
    with open(out_file, 'w') as fp:
        json.dump(relation, fp, indent=4)

    print("Pipeline completed")
    print(f"Final output is written to {out_file}")

    return relation


def main():
    parser = ArgumentParser(
        description="Automated Normalization Checker CLI: Decompose to 2NF/3NF")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--database", "-db", type=str, help="Database name")
    group.add_argument("--schema", "-s", type=str, help="File path to schema")

    parser.add_argument("--dependencies", "-d", required=True,
                        type=str, help="File path of dependencies")
    parser.add_argument(
        "--level", "-l", choices=["2NF", "3NF"], help="Normalization level - 2NF or 3NF")
    parser.add_argument("--out_prefix", "-f", type=str,
                        help="Prefix for output file")

    args = parser.parse_args()

    try:
        if args.database:
            print(f"Establishing connection to database: {args.database}")
            # print("Extracting schema from database...")
            schema = get_schema(args.database)
        else:
            print(f"Extracting schema from schema file: {args.schema}")
            schema = extract_json(args.schema)

        dependencies = extract_json(args.dependencies)

        relation = pipeline(schema=schema, dependencies=dependencies,
                            normalization_level=args.level, out_prefix=args.out_prefix)

        print("Done!")

    except Exception as e:
        print("An error occurred while running the normalization pipeline.")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
