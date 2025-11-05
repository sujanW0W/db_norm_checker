from sqlalchemy import MetaData
from connection import get_db_connection
import json
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Extract schema from the given database")
    parser.add_argument("--db_name", "-d", type=str, help="Database name")
    parser.add_argument("--file_name", "-f", type=str,
                        help="Filename if the schema has to be written into a file", default=None)

    args = parser.parse_args()

    extracted_schema = get_schema(args.db_name)

    if args.file_name:
        with open(f"{args.file_name}.json", 'w') as fp:
            json.dump(extracted_schema, fp, indent=4)

        print(f"Wrote into the {args.file_name}")

    else:
        schema_json = json.dumps(extracted_schema, indent=4)
        print(schema_json)


def get_schema(db_name):
    db_schema = {}

    engine = get_db_connection(db_name)

    metadata = MetaData()
    metadata.reflect(bind=engine)

    print(f"Database: {db_name}")

    for table_name in metadata.tables:
        table = metadata.tables[table_name]
        print("Table: ", table)

        db_schema[table.name] = {}

        for column in table.columns:
            db_schema[table.name][column.name] = {
                "type": column.type.__class__.__name__,
                "PK": column.primary_key,
                "Unique": column.unique,
                "Nullable": column.nullable,
                "FKs": [{"name": fk.name, "references": f"{fk.column.table}.{fk.column.name}"} for fk in column.foreign_keys]
            }

    return db_schema


if __name__ == "__main__":
    main()
