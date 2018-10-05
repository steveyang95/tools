import os
import sys
import time
import requests
import json
import pprint
import collections
import csv
import datetime
import argparse
import textwrap
import string
import random

def write_to_files(csv_keys, file_name, data, path_to_file=None):
    if path_to_file:
        file_name = os.path.expanduser("{}/{}".format(path_to_file, file_name))

    _out("Writing out to file {}.csv".format(file_name))
    with open("{}.csv".format(file_name), 'w') as csvfile:
        dict_writer = csv.DictWriter(csvfile, list(csv_keys))
        dict_writer.writeheader()
        dict_writer.writerows(data)


def id_generator(size=9, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _out(msg, title=None):
    title = title if title else "MESSAGE"
    print("\n[{}] {}".format(title, msg))


keys = ["AccountId","OAuthProvider","Company","Complete","ContactEmail","DisplayEmail","FeatureElephant","email"]

entries = []
for i in range(200000):
    if i % 5000 == 0:
        _out("Passed {} entries".format(i))
    item = {"AccountId": id_generator(size=5),
            "email": "{}@gmail.com".format(id_generator())}
    entries.append(item)

_out("Ready with {} entries".format(len(entries)))
write_to_files(keys, "bubble_users", entries)
_out("Done!")
