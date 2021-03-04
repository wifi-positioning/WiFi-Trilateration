from flask import Flask
from flask import request
from addon.parse_dumps import DumpParser
import redis
import json

# from engine import Engine

# global apiFlaskServer
class APIv1:

    apiFlaskServer = None
    srv_engine = None
    srv_locator = None
    r = redis.Redis()
    def __init__(self, fs, srv_engine, srv_locator):
        self.apiFlaskServer = fs
        self.srv_engine = srv_engine
        self.srv_locator = srv_locator

        @self.apiFlaskServer.route("/api/v1/ping", methods=['GET'])
        def pingAPIv1():
            return "pong"

        @self.apiFlaskServer.route("/api/v1/get/vector", methods=['GET'])
        def getVectorAPIv1():
            mac = request.args.get('mac')
            if not mac:
                return "[1]"
            vector = self.r.get(mac)
            if not vector:
                return "[2]"
            return vector
            # probsup_dumps = srv_engine._thread_pool.map(srv_engine._fetch_probsup_dump, srv_engine.ap_list)
            # mac_to_vector = DumpParser().parse(srv_locator, probsup_dumps)
            # mac_to_position = {mac:srv_locator._locate(vector[0]) for mac,vector in mac_to_vector.items()}
            # for mac,rssi in mac_to_vector.items():
            #     self.r.set(mac, json.dumps(rssi))
            # return mac_to_position

        @self.apiFlaskServer.route("/api/v1/set/vector", methods=['POST'])
        def setVectorAPIv1():
            j = request.get_json()
            print(j)
            key = j['key']
            val = j['val']
            if not key and not val:
                return "Error"
            self.r.set(key, val)
            foo(key)
            return "Updated successfully"


        def foo(mac):
            raw_data = self.r.get(mac).decode('utf-8').split(";")
            db_data = [0 for idx in range(len(raw_data))]
            for idx in range(len(raw_data)):
                db_data[idx] = raw_data[idx].split(",")
            print(db_data)
            self.r.set(mac, "yup")

    def run(self):
        self.apiFlaskServer.run(host='0.0.0.0', port=8080)
def initRoutesAPIv1():
    pass
