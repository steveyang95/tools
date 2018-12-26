import os
import mimetypes
import falcon
from falcon_cors import CORS
import json


cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)
api = falcon.API()


class Index:
    def on_get(self, req, res):
        with open("hi.txt", "a+") as f:
            f.write("got here")
        res.body = json.dumps({"status": "OK"})


api.add_route("/", Index())
