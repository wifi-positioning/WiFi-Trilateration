from multiprocessing.dummy import Pool
from multiprocessing import Queue
from locator import Locator
from time import sleep
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
from socket import timeout
from APIv1 import APIv1
from flask import Flask


global flaskServer

class Engine:
    def __init__(self, config):
        self.ap_list = config["ap_properties"]
        self.poll_interval = config["monitoring_properties"]["poll_interval"]
        self._thread_pool = Pool(len(config["ap_properties"]))
        self._locator_queue = Queue()
        self._locator = Locator(self._locator_queue, config)

    # def _fetch_probsup_dump(self, ap):
    #     # client = SSHClient()
    #     # client.set_missing_host_key_policy(AutoAddPolicy())
    #     # try:
    #     #     client.connect(hostname=ap["ip_address"], port=ap["ssh_port"],
    #     #                    username=ap["login"], password=ap["password"], timeout=3)
    #     # except (NoValidConnectionsError, timeout):
    #     #     return ""
    #     # rssi_dump = [None for cnt in range(2)]
    #     # if ap["ap_type"] == 0:
    #     #     rssi_dump[0] = 0
    #     #     connect = client.invoke_shell()
    #     #     connect.send("wl -i %s probsup_dump\n" % ap["monitoring_interface"])
    #     #     while not connect.recv_ready():
    #     #         sleep(0.1)
    #     #     rssi_dump[1] = connect.recv(50000).decode()
    #     #     connect.close()
    #     # elif ap["ap_type"] == 1:
    #     #     rssi_dump[0] = 1
    #     #     (stdin, stdout, stderr) = client.exec_command("monitoring clients hw-addr rssi-1\n")
    #     #     rssi_dump[1] = stdout.readlines()
    #     rssi_dump = "ea: 60:ab:67:fe:d1:c5, state: 1, cycle: 1, rssi: -76, age: 5\
    #                 ea: ce:35:6f:17:9c:6f, state: 1, cycle: 1, rssi: -77, age: 94\
    #                 ea: da:a1:19:58:78:5b, state: 1, cycle: 1, rssi: -75, age: 178\
    #                 ea: 62:a3:47:b4:9e:5a, state: 1, cycle: 1, rssi: -60, age: 172\
    #                 ea: da:a1:19:60:f4:9f, state: 1, cycle: 1, rssi: -58, age: 172\
    #                 ea: 6c:e8:c6:89:06:a9, state: 1, cycle: 1, rssi: -77, age: 93\
    #                 ea: 8c:45:00:2a:93:39, state: 1, cycle: 1, rssi: -76, age: 90\
    #                 ea: b6:1a:41:eb:7e:9a, state: 1, cycle: 1, rssi: -77, age: 85\
    #                 ea: f2:f4:bc:ad:57:59, state: 1, cycle: 1, rssi: -70, age: 84\
    #                 ea: 4e:24:f4:68:1e:dd, state: 1, cycle: 1, rssi: -64, age: 84\
    #                 ea: 04:79:70:87:79:d5, state: 1, cycle: 1, rssi: -62, age: 76\
    #                 ea: 9a:aa:56:f9:5a:3d, state: 1, cycle: 1, rssi: -81, age: 65"
    #         # connect.send("monitoring clients hw-addr rssi-1\n")
    #     # client.close()
    #     return rssi_dump

    def shutdown(self):
        self._thread_pool.close()
        self._thread_pool.join()
        # self._locator.join()
        # self._locator.terminate()

    def run(self):
        self._locator.start()
        flaskServer = Flask(__name__)
        self.api = APIv1(flaskServer, self, self._locator)
        self.api.run()
        # while True:
        #     probsup_dumps = self._thread_pool.map(self._fetch_probsup_dump, self.ap_list)
        #     self._locator_queue.put(probsup_dumps)
        #     sleep(self.poll_interval)
