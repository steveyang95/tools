import os
import sys
import time
import requests
import string
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tools.stopwatch as stopwatch

# Overall Users API Endpoint
USERS_VERSION_TEST_URL = "https://{name}/version-test/api/1.1/wf/"
USERS_LIVE_URL = "https://{name}/api/1.1/wf/"

HEADER = {"Authorization": "Bearer {token}"}
PARAMS = {}

CLOCK = stopwatch.Clock()


def create_users(users, live=False, endpoint="create_user"):
    _out("Starting to populate bubble database with {} users".format(len(users)))
    i = 0
    session = requests.Session()
    base_url = USERS_VERSION_TEST_URL if not live else USERS_LIVE_URL
    url = "{}/{}".format(base_url, endpoint)
    for user in users:
        params = {"password": user['password'],
                  "email": user['email'],
                  "DisplayEmail": user['email']}

        if i % 5000 == 0:
            _out("curl -X POST {} -H 'application/json' -d {}".format(url, params), title="CURL")
            _out("Created {} users".format(i))

        if i == 0:
            CLOCK.start_stopwatch("1")
            CLOCK.start_stopwatch("10")
            CLOCK.start_stopwatch("100")
            CLOCK.start_stopwatch("1000")

        r = session.post(url, json=params, headers=HEADER)
        exp = 0
        while r.status_code != 200:
            _out("Code is {}. Will wait for a bit and then try again. Try {}".format(r.status_code, exp), "STATUS CODE")
            print(r.json())
            time.sleep(2**exp)
            exp += 1
            r = session.post(url, json=params, headers=HEADER)
            if exp == 5:
                _out("Failure to exponentially back off. Please try again")
                return
        i += 1
        if i % 1 == 0:
            CLOCK.stop_stopwatch("1")
            CLOCK.start_stopwatch("1")
        if i % 10 == 0:
            CLOCK.stop_stopwatch("10")
            CLOCK.start_stopwatch("10")
        if i % 100 == 0:
            CLOCK.stop_stopwatch("100")
            CLOCK.start_stopwatch("100")
        if i % 1000 == 0:
            CLOCK.stop_stopwatch("1000")
            CLOCK.start_stopwatch("1000")

        if i % 2000 == 0:
            for sw in CLOCK.get_stopwatch_keys():
                _out(CLOCK.get_average_time_elapsed(sw), "STATS {}".format(sw))

    for sw in CLOCK.get_stopwatch_keys():
        _out(CLOCK.get_average_time_elapsed(sw), "STATS {}".format(sw))

    _out("Finished creating users!")


def create_dummy_users(size):
    _out("Creating dummy users of size {}".format(size))
    users = []
    for i in range(size):
        users.append({"email": "{}@gmail.com".format(id_generator()), "password": id_generator(5)})
    _out("Finished creating dummy users of size {}".format(size))
    return users


def id_generator(size=9, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _out(msg, title=None):
    title = title if title else "MESSAGE"
    print("\n[{}] {}".format(title, msg))


create_users(create_dummy_users(200000))


