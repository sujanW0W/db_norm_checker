from extract_schema import get_schema
from read_json import extract_json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_name", "-d", type=str,
                        help="Database name whose schema is to be extracted")
    parser.add_argument("--file_name", "-f", type=str,
                        help="File containing functional dependencies")
    args = parser.parse_args()

    schema = get_schema(args.db_name)
    dependencies = extract_json(args.file_name)

    verify_schema_dependencies(schema, dependencies)


def verify_schema_dependencies(schema, dependencies):
    table_columns = {}
    fd_details = {}

    for (table, column_dict) in schema.items():
        table_columns[table] = []
        for (column_name, column_details) in column_dict.items():
            table_columns[table].append(column_name)

    # print(table_columns)

    for (table, fds) in dependencies.items():
        fd_details[table] = []
        fd_details[table].extend(fds.keys())
        for val_list in fds.values():
            fd_details[table].extend(val_list)
        spread_composite_keys = []
        for val in fd_details[table]:
            spread_composite_keys.extend([v.strip() for v in val.split(',')])
        fd_details[table] = list(set(spread_composite_keys))

    # print(fd_details)

    for (table, cols) in fd_details.items():
        if table not in table_columns.keys():
            raise ValueError(f"Table {table} is not in schema")

        if not set(cols).issubset(table_columns[table]):
            raise ValueError(
                f"Columns mismatch: \n FD: {cols}\nSchema: {table}: {table_columns[table]} ")

    print("All attributes in Functional dependencies are valid.")


if __name__ == "__main__":
    main()
