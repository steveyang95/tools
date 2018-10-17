import string
import random

from csv_helper import write_to_files


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
