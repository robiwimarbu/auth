import json

from flask import make_response

class Utils:
    def nice_json(self,arg, status = 200):
        response = make_response(json.dumps(arg, sort_keys = True, indent=4), status)
        response.headers['Content-type'] = "application/json"
        return response