import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData, Table

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_db_connection(db_uri):
    try:
        # engine = create_engine(DB_URI, echo=True)
        engine = create_engine(db_uri)
        print("Connection established successfully")
        return engine

    except Exception as e:
        print("Failed to establish connection")
        raise Exception(e)


def main():
    databases = []
    db_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"

    for database in databases:
        print(f"\n--- {database} ---\n")
        db_uri_instance = f"{db_uri}{database}"

        engine = get_db_connection(db_uri_instance)

        # inspector = inspect(engine)
        # table_names = inspector.get_table_names()

        metadata = MetaData()
        metadata.reflect(bind=engine)

        print("Tables Information")

        for table_name in metadata.tables:
            table = metadata.tables[table_name]
            print("Table: ", table)

            print(f"Columns: {table.columns}")
            print(f"Primary key: {table.primary_key}")
            print(f"Foreign key: {table.foreign_keys}")

            # for column in table.columns:
            #     print(
            #         f"Column: {column.name}, Column type: {column.type}, Column Nullable: {column.nullable}")

        print()


if __name__ == "__main__":
    main()
