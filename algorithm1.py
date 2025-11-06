"""
    Algorithm to determine partial and full dependencies
"""

from read_json import extract_json
import copy
import json


def get_full_and_partial_fd(fd_file_name, keys_dict):
    # Consider Minimal cover set of F (Need another algorithm to get Minimal cover)
    Fm = {}
    # Full dependencies in Fm
    Ff = {}
    # Partial dependencies in Fm
    Fp = {}

    # First, lets read the given dependencies

    dependencies = extract_json(fd_file_name)

    Fm = copy.deepcopy(dependencies)
    Ff = copy.deepcopy(Fm)

    # I need to find a way to determine the candidate key in the table before I run this algorithm
    # candidate_key = "student_id, course_id"
    # keys = ["student_id, course_id"]

    for table in Fm:
        Fp[table] = {}
        # print(f"Table: {table}")

        # Check for partial dependencies
        # print("Check for Partial FD")
        for (lhs, rhs_list) in Fm[table].items():
            if lhs not in Fp[table].keys():
                Fp[table][lhs] = []
            for rhs in rhs_list:
                # print(f"{lhs} -> {rhs}")

                if lhs != keys_dict[table]["candidate_key"] and lhs in keys_dict[table]["candidate_key"].split(', ') and rhs not in keys_dict[table]["keys"]:
                    # print("Partial FD")
                    Fp[table][lhs].append(rhs)
                    Ff[table][lhs].remove(rhs)

        # Check for transitive dependencies (For 2NF, put transitive dependencies along with partial dependencies)
        # print("Check for Transitive FD")
        for (lhs, rhs_list) in copy.deepcopy(Ff[table]).items():
            if lhs not in Fp[table].keys():
                Fp[table][lhs] = []
            for rhs in rhs_list:
                # print(f"{lhs} -> {rhs}")

                if lhs not in keys_dict[table]["keys"] and any([lhs in Fp_rhs_list for Fp_rhs_list in Fp[table].values()]):
                    # print("Transitive FD")
                    Fp[table][lhs].append(rhs)
                    Ff[table][lhs].remove(rhs)

        Fp[table] = dict([(k, v) for k, v in Fp[table].items() if len(v) > 0])
        Ff[table] = dict([(k, v) for k, v in Ff[table].items() if len(v) > 0])

    return Ff, Fp


def decompose_to_2NF(schema_file_name, dependencies_file_name):
    R = extract_json(schema_file_name)
    keys_dict = {}
    for table, col_dict in R.items():
        candidate_keys_list = []
        keys_list = []
        for col, col_details in col_dict.items():
            if col_details['PK']:
                candidate_keys_list.append(col)
                keys_list.append(col)
        keys_dict[table] = {
            "candidate_key": ', '.join(candidate_keys_list),
            "keys": keys_list
        }
    # print(keys_dict)

    Ff, Fp = get_full_and_partial_fd(dependencies_file_name, keys_dict)
    print(f"Ff: {Ff}")
    print(f"Fp: {Fp}")
    R_2NF = {}

    # Create relations for partial dependencies
    for table, fds in copy.deepcopy(Fp).items():
        # print(f"Table: {table}")
        for lhs, rhs_list in fds.items():
            if lhs != keys_dict[table]["candidate_key"] and lhs in keys_dict[table]["candidate_key"]:
                R_2NF[f"{table}_{lhs}"] = {}
                # Assign columns related to the lhs
                for col, col_details in R[table].items():
                    if col == lhs:
                        R_2NF[f"{table}_{lhs}"][col] = col_details
                        R_2NF[f"{table}_{lhs}"][col]['PK'] = True

                    if col in rhs_list:
                        R_2NF[f"{table}_{lhs}"][col] = col_details

                Fp[table] = dict([(k, v)
                                 for k, v in Fp[table].items() if k != lhs])

        # print(f"Fp after partial FD: {Fp}")
    print(
        f"R_2NF: {dict([(table, col_details.keys()) for table, col_details in R_2NF.items()])}")

    # Add columns to relations having transitive dependencies
    for table, fds in copy.deepcopy(Fp).items():
        # print(f"Table: {table}")
        for lhs, rhs_list in fds.items():
            for table_name, col_dict in R_2NF.items():
                if table != table_name.split('_')[0]:
                    continue
                if lhs in col_dict.keys():
                    for rhs in rhs_list:
                        R_2NF[table_name][rhs] = R[table][rhs]

            Fp[table] = dict([(k, v)
                              for k, v in Fp[table].items() if k != lhs])

    Fp = dict((k, v) for k, v in Fp.items() if len(v.keys()) > 0)

    # print(f"Fp after transitive FD: {Fp}")
    print(
        f"R_2NF: {dict([(table, col_details.keys()) for table, col_details in R_2NF.items()])}")

    # Relation for full FD
    # Remove non-key attributes from Full FD that are in other relations
    non_key_attributes = dict()

    for table, column_dict in R_2NF.items():
        for col, col_details in column_dict.items():
            if not col_details['PK'] and not col_details['Unique']:
                if table.split("_")[0] in non_key_attributes.keys():
                    non_key_attributes[table.split("_")[0]].append(col)
                else:
                    non_key_attributes[table.split("_")[0]] = [col]

    print(f"non_key_attributes: {non_key_attributes}")

    for table, fds in copy.deepcopy(Ff).items():
        for lhs, rhs_list in fds.items():
            for rhs in rhs_list:
                if rhs in non_key_attributes.get(table, []):
                    Ff[table][lhs].remove(rhs)

    # Check if any non-key attributes in Full FD is in other relations
    Xf = dict([(table, [*col_dict.keys(), *[col for cols in col_dict.values()
              for col in cols]]) for table, col_dict in Ff.items()])
    print(f"Xf: {Xf}")

    Ff_attributes_check = any(col in non_key_attributes.get(
        table, []) for table, cols in Xf.items() for col in cols)

    if Ff_attributes_check:
        raise ValueError("There is some issue with Full FD")

    for table, fds in copy.deepcopy(Ff).items():
        for lhs, rhs_list in fds.items():
            R_2NF[f"{table}_{lhs.replace(', ', '_')}"] = {}
            for col in [*lhs.split(", "), *rhs_list]:
                # for col, col_details in R[table].items():
                R_2NF[f"{table}_{lhs.replace(', ', '_')}"][col] = R[table][col]

            Ff[table] = dict([(k, v)
                             for k, v in Ff[table].items() if k != lhs])

    Ff = dict([(k, v) for k, v in Ff.items() if len(v.keys()) > 0])

    return R_2NF


if __name__ == "__main__":
    # Ff, Fp = get_full_and_partial_fd("./dependencies.json")
    # print(f"\nFull functional dependencies: {Ff}")
    # print(f"\nPartial functional dependencies: {Fp}")

    r_2F = decompose_to_2NF("./test_schema_2.json",
                            "./test_dependencies_2.json")

    with open("test_db_2NF.json", 'w') as fp:
        json.dump(r_2F, fp, indent=4)
