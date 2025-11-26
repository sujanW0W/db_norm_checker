import os
import re
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Read json")
    parser.add_argument("--file", type=str,
                        help="Provide the path to json file")

    args = parser.parse_args()

    extracted_data = extract_json(args.file)
    print(extracted_data)


def extract_json(filename):
    json_file_regex = r"^.+\.json$"

    if not re.match(json_file_regex, filename):
        raise Exception("Only json file is supported")

    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data

    except FileNotFoundError:
        raise f"Error: File {filename} not found"
    except Exception as e:
        raise f"Exception Raised: {e}"


if __name__ == "__main__":
    main()
