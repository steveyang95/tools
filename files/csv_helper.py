import os
import sys
import json
import csv
import pprint


def csv_to_dict(file_name):
    """
    Converts CSV contents to a Dictionary.
    First line in CSV must be Headers.

    INPUT:
        file_name (str): Full path to file

    OUTPUT:
        (dict)
    """
    entries = []
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        headers = reader.next()
        _out(headers, "csv_to_dict - HEADERS")
        for row in reader:
            entry = {}
            for i in range(len(headers)):
                entry[headers[i]] = row[i]
            entries.append(entry)
    return entries


def write_to_files(csv_keys, file_name, data, path_to_file=None):
    """
    Writes to {path_to_file}/{file_name}.csv with data and csv_keys as the header.

    INPUT:
        csv_keys (list)
        file_name (str)
        data (list): List of dictionaries
        path_to_file (str)
    """
    if path_to_file:
        file_name = os.path.expanduser("{}/{}".format(path_to_file, file_name))

    _out("Writing out to file {}.csv".format(file_name))
    with open("{}.csv".format(file_name), 'w') as csvfile:
        dict_writer = csv.DictWriter(csvfile, list(csv_keys))
        dict_writer.writeheader()
        dict_writer.writerows(data)


def _out(msg, title=None):
    title = title if title else "MESSAGE"
    print("\n[{}] {}".format(title, msg))

