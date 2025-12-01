"""
    Algorithm to determine partial and full dependencies
"""

from .read_json import extract_json
import copy
import json
from collections import defaultdict
from argparse import ArgumentParser


def extract_keys(schema):
    keys_dict = {}
    for table, col_dict in schema.items():
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
    return keys_dict


def get_full_partial_transitive_fd(dependencies, keys_dict):
    # To generalize, add space after the comma for composite keys
    dependencies = dict([(table, dict([(lhs.replace(', ', ',').replace(',', ', '), rhs_list)
                        for lhs, rhs_list in fds.items()])) for table, fds in dependencies.items()])

    print("\n--- FDs ---")
    # Consider Minimal cover set of F (Need another algorithm to get Minimal cover)
    Fm = defaultdict(lambda: defaultdict(list))
    # Full dependencies in Fm
    Ff = defaultdict(lambda: defaultdict(list))
    # Partial dependencies in Fm
    Fp = defaultdict(lambda: defaultdict(list))
    # Transitive dependencies
    Td = defaultdict(lambda: defaultdict(list))

    Fm = copy.deepcopy(dependencies)
    Ff = copy.deepcopy(Fm)

    print(Fm)

    for table in Fm:
        # print(f"Table: {table}")

        # Check for partial dependencies
        # print("Check for Partial FD")
        for (lhs, rhs_list) in Fm[table].items():
            for rhs in rhs_list:
                # print(f"{lhs} -> {rhs}")

                if lhs != keys_dict[table]["candidate_key"] and lhs in keys_dict[table]["candidate_key"].split(', ') and rhs not in keys_dict[table]["keys"]:
                    # print("Partial FD")
                    Fp[table][lhs].append(rhs)
                    if rhs in Ff[table][keys_dict[table]["candidate_key"]]:
                        Ff[table][keys_dict[table]
                                  ["candidate_key"]].remove(rhs)

        # Check for transitive dependencies (For 2NF, put transitive dependencies along with partial dependencies)
        # print("Check for Transitive FD")
        for (lhs, rhs_list) in copy.deepcopy(Ff[table]).items():
            for rhs in rhs_list:
                # print(f"{lhs} -> {rhs}")

                if len(Fp[table]):
                    if lhs not in keys_dict[table]["keys"] and any([lhs in Fp_rhs_list for Fp_rhs_list in Fp[table].values()]):
                        # print("Transitive FD")
                        Td[table][lhs].append(rhs)
                        Fp[table][lhs].append(rhs)
                        Ff[table][keys_dict[table]
                                  ["candidate_key"]].remove(rhs)
                        del Ff[table][lhs]
                else:
                    if lhs not in keys_dict[table]["keys"] and any([lhs in Ff_rhs_list for Ff_rhs_list in Ff[table].values()]):
                        Td[table][lhs].append(rhs)

    dependencies_dict = dict([('Ff', Ff), ('Fp', Fp), ('Td', Td)])
    return dependencies_dict


def decompose_to_2NF(relation, keys_dict, dependencies):
    print("\n--- 2NF ---")

    Ff, Fp, Td = dependencies['Ff'], dependencies['Fp'], dependencies['Td']

    # print(f"Ff: {Ff}")
    # print(f"Fp: {Fp}")
    # print(f"Td: {Td}")

    relation_2NF = defaultdict(lambda: defaultdict(dict))

    # Create relations for partial dependencies
    for table, fds in copy.deepcopy(Fp).items():
        # print(f"Table: {table}")
        for lhs, rhs_list in fds.items():
            if lhs != keys_dict[table]["candidate_key"] and lhs in keys_dict[table]["candidate_key"]:
                # Assign columns related to the lhs
                for col, col_details in relation[table].items():
                    if col == lhs:
                        relation_2NF[f"{table}_{lhs}"][col] = col_details
                        relation_2NF[f"{table}_{lhs}"][col]['PK'] = True

                    if col in rhs_list:
                        relation_2NF[f"{table}_{lhs}"][col] = col_details

                Fp[table] = dict([(k, v)
                                 for k, v in Fp[table].items() if k != lhs])

    # Add columns to relations having transitive dependencies
    for table, fds in copy.deepcopy(Fp).items():
        # print(f"Table: {table}")
        for lhs, rhs_list in fds.items():
            for table_name, col_dict in relation_2NF.items():
                if table != table_name.split('_')[0]:
                    continue
                if lhs in col_dict.keys():
                    for rhs in rhs_list:
                        relation_2NF[table_name][rhs] = relation[table][rhs]

            Fp[table] = dict([(k, v)
                              for k, v in Fp[table].items() if k != lhs])

    Fp = dict((k, v) for k, v in Fp.items() if len(v.keys()) > 0)

    # Relation for full FD
    # Remove non-key attributes from Full FD that are in other relations
    non_key_attributes = dict()

    for table, column_dict in relation_2NF.items():
        for col, col_details in column_dict.items():
            if not col_details['PK'] and not col_details['Unique']:
                if table.split("_")[0] in non_key_attributes.keys():
                    non_key_attributes[table.split("_")[0]].append(col)
                else:
                    non_key_attributes[table.split("_")[0]] = [col]

    # print(f"non_key_attributes: {non_key_attributes}")

    for table, fds in copy.deepcopy(Ff).items():
        for lhs, rhs_list in fds.items():
            for rhs in rhs_list:
                if rhs in non_key_attributes.get(table, []):
                    Ff[table][lhs].remove(rhs)

    # Check if any non-key attributes in Full FD is in other relations
    Xf = dict([(table, [*col_dict.keys(), *[col for cols in col_dict.values()
              for col in cols]]) for table, col_dict in Ff.items()])
    # print(f"Xf: {Xf}")

    Ff_attributes_check = any(col in non_key_attributes.get(
        table, []) for table, cols in Xf.items() for col in cols)

    if Ff_attributes_check:
        raise ValueError("There is some issue with Full FD")

    for table, fds in copy.deepcopy(Ff).items():
        for lhs, rhs_list in fds.items():
            Ff[table] = dict([(k, v)
                             for k, v in Ff[table].items() if k != lhs])

            if lhs != keys_dict[table]["candidate_key"]:
                continue
            for col in [*lhs.split(", "), *rhs_list]:
                relation_2NF[f"{table}_{lhs.replace(', ', '_')}"][col] = relation[table][col]

    Ff = dict([(k, v) for k, v in Ff.items() if len(v.keys()) > 0])

    # Transitive dependencies without partial dependencies
    for table, fds in Td.items():
        for lhs, rhs_list in fds.items():
            for table_name, col_dict in relation_2NF.items():
                if table != table_name.split('_')[0]:
                    continue
                if lhs in col_dict.keys():
                    for rhs in rhs_list:
                        if rhs not in relation_2NF[table_name]:
                            relation_2NF[table_name][rhs] = relation[table][rhs]

    print(dict([(table, table_dict.keys())
          for table, table_dict in relation_2NF.items()]))

    dependencies = {
        'Ff': Ff,
        'Fp': Fp,
        'Td': Td
    }

    return relation_2NF, dependencies


def decomponse_to_3NF(relation, dependencies):
    print("\n--- 3NF ---")
    Ff, Fp, Td = dependencies['Ff'], dependencies['Fp'], dependencies['Td']

    # Check if the relation is in 2NF through Fp
    # print(f"Ff: {Ff}")
    # print(f"Fp: {Fp}")
    # print(f"Td: {Td}")
    if len(Fp):
        print("The relation is not in 2NF")
        return

    copied_relation = copy.deepcopy(relation)
    for table, fds in copy.deepcopy(Td).items():
        for lhs, rhs_list in fds.items():
            for table_2NF, col_dict in copied_relation.items():
                if table in table_2NF and all([col in col_dict.keys() for col in [lhs, *rhs_list]]):
                    temp = defaultdict(lambda: defaultdict)
                    for col in [lhs, rhs_list[0]]:
                        temp[col] = col_dict[col]

                    relation[f"{table}_{lhs}_{rhs_list[0]}"] = temp
                    del relation[table_2NF][rhs_list[0]]

            Td[table] = dict([(k, v)
                             for k, v in Td[table].items() if k != lhs])

    Td = dict([(k, v) for k, v in Td.items() if len(v)])

    print(dict([(k, v.keys()) for k, v in relation.items()]))

    return relation


def main():
    args = ArgumentParser()
    args.add_argument("--schema", "-s", required=True, type=str,
                      help="Filename of the schema")
    args.add_argument("--dependencies", "-d", required=True, type=str,
                      help="Filename containing functional dependencies")

    parser = args.parse_args()

    schema = extract_json(parser.schema)
    dependencies = extract_json(parser.dependencies)

    keys = extract_keys(schema)

    dependencies_dict = get_full_partial_transitive_fd(dependencies, keys)

    print(dependencies_dict)

    relation_2NF, dependencies_dict = decompose_to_2NF(
        schema, keys, dependencies_dict)

    relation_3NF = decomponse_to_3NF(relation_2NF, dependencies_dict)

    with open(f"3NF_relation.json", 'w') as fp:
        json.dump(relation_3NF, fp, indent=4)


if __name__ == "__main__":
    main()
