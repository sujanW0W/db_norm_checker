#!/bin/bash

# Two ways to execute

# 1. python -m db_normalizer -db DB_NAME -d DEPENDENCIES -l [2NF/3NF] -f FILE_NAME

# 2. db-normalizer -db DB_NAME -d DEPENDENCIES -l [2NF/3NF] -f FILE_NAME

db-normalizer -db ECOMMERCE -d ./tests/dependencies_foreign.json -l 3NF -f final_test