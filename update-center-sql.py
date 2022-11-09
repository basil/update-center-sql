import argparse
import io
import json
import logging
import os
import re
import sqlite3
import urllib.request


def parse_json(update_center):
    with urllib.request.urlopen(update_center) as response, io.TextIOWrapper(
        response, encoding="utf-8"
    ) as text:
        lines = text.readlines()
        if (
            len(lines) > 2
            and lines[0].rstrip() == "updateCenter.post("
            and lines[2].rstrip() == ");"
        ):
            data = lines[1].rstrip()
        else:
            data = lines[0].rstrip()
        return json.loads(data)


def import_data(json_data, output):
    if os.path.exists(output):
        logging.warning("Removing existing output file: " + output)
        os.remove(output)
    with sqlite3.connect(output) as db:
        create_table("root", json_data, db, True)
        import_table("root", json_data, db, True)


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def create_table(table_name, table_data, db, is_root):
    columns = set()
    for key, value in table_data.items():
        if isinstance(value, dict):
            if is_root:
                create_table(key, value, db, False)
            else:
                columns.add("name")
                for key2 in value:
                    columns.add(camel_to_snake(key2))
        elif (
            isinstance(value, int) or isinstance(value, list) or isinstance(value, str)
        ):
            columns.add(camel_to_snake(key))
    if columns:
        create_stmt = f"CREATE TABLE {table_name}({', '.join(sorted(columns))})"
        db.execute(create_stmt)


def import_table(table_name, table_data, db, is_root):
    row = {}
    for key, value in table_data.items():
        if isinstance(value, dict):
            if is_root:
                import_table(key, value, db, False)
            else:
                row2 = {}
                row2["name"] = key
                for key2, value2 in value.items():
                    if isinstance(value2, int) or isinstance(value2, str):
                        row2[key2] = value2
                    elif isinstance(value2, list):
                        row2[key2] = str(value2)
                if row2:
                    insert_row(table_name, row2, db)
        elif isinstance(value, int) or isinstance(value, str):
            row[key] = value
        elif isinstance(value, list):
            row[key] = str(value)
    if row:
        insert_row(table_name, row, db)


def insert_row(table_name, row, db):
    row2 = {camel_to_snake(key): value for key, value in row.items()}
    insert_stmt = "INSERT INTO " + table_name + " ("
    insert_stmt += ", ".join(sorted(row2.keys()))
    insert_stmt += ") VALUES ("
    insert_stmt += ",".join([":" + column for column in sorted(row2.keys())])
    insert_stmt += ")"
    db.execute(insert_stmt, row2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-o",
        "--output",
        default="update-center.db",
        help="The name of the SQLite database to create.",
    )
    parser.add_argument(
        "-u",
        "--update-center",
        default="https://updates.jenkins.io/update-center.json",
        help="The Update Center URL to fetch plugins from.",
    )
    args = parser.parse_args()
    json_data = parse_json(args.update_center)
    import_data(json_data, args.output)
    os.execlp("sqlite3", "sqlite3", os.path.abspath(args.output))
