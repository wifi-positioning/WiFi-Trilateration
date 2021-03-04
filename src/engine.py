from multiprocessing.dummy import Pool
from multiprocessing import Queue
from locator import Locator
from time import sleep
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from socket import timeout

class Engine:

	def __init__(self, config):
		self.ap_list = config["ap_properties"]
		self.poll_interval = config["monitoring_properties"]["poll_interval"]
		self._thread_pool = Pool(len(config["ap_properties"]))
		self._locator_queue = Queue()
		self._mode = config["method"]
		self._locator = Locator(self._locator_queue, config, self._mode)

	def _fetch_probsup_dump(self, ap):
		client = SSHClient()
		client.set_missing_host_key_policy(AutoAddPolicy())
		try:
			client.connect(hostname=ap["ip_address"], port=ap["ssh_port"],
				           username=ap["login"], password=ap["password"], timeout=3)
		except (NoValidConnectionsError, SSHException, timeout):
			print(ap["ip_address"])
			return ""
		rssi_dump = [None for cnt in range(2)]
		if ap["ap_type"] == 0:
			rssi_dump[0] = 0
			connect = client.invoke_shell()
			connect.send("wl -i %s probsup_dump\n" % ap["monitoring_interface"])
			while not connect.recv_ready():
				sleep(0.1)
			rssi_dump[1] = connect.recv(50000).decode()
			connect.close()
		elif ap["ap_type"] == 1:
			rssi_dump[0] = 1
			(stdin, stdout, stderr) = client.exec_command("monitoring clients hw-addr rssi-1\n")
			rssi_dump[1] = stdout.readlines()
			# connect.send("monitoring clients hw-addr rssi-1\n")
		client.close()
		return rssi_dump

	def shutdown(self):
		self._thread_pool.close()
		self._thread_pool.join()
		self._locator.terminate()
		self._locator.join()

	def run(self):
		self._locator.start()
		while True:
			probsup_dumps = self._thread_pool.map(self._fetch_probsup_dump, self.ap_list)
			self._locator_queue.put(probsup_dumps)
			sleep(self.poll_interval)
