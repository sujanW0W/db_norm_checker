import os
import re
import json
import argparse

parser = argparse.ArgumentParser(description="Read json")
parser.add_argument("--file", type=str, help="Provide the path to json file")

args = parser.parse_args()

json_file_regex = r"^.+\.json$"

if not re.match(json_file_regex, args.file):
    raise Exception("Only json file is supported")

try:
    with open(args.file, 'r') as file:
        data = json.load(file)
    print(data)

except FileNotFoundError:
    print(f"Error: File {args.file} not found")
except Exception as e:
    print(f"Exception Raised: {e}")
