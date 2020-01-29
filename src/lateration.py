from multiprocessing import Process
from gui import Window
from numpy import zeros, delete, unravel_index, any as is_not_all_zeros
from texttable import Texttable
from subprocess import call
from re import findall
from tkinter import *

class Lateration(Process):

	def __init__(self, locator_queue, config, clr_arr):
		super().__init__()
		self._clr_arr = clr_arr
		self._locator_queue = locator_queue
		self._ap_amount = len(config["ap_properties"])
		self.mac_to_name = config["monitoring_properties"]["users"]

	def _form_mac_to_vector_matchings(self, probsup_dumps):
		mac_to_vector = {mac:zeros(self._ap_amount) for mac in self.mac_to_name}
		for idx,probsup_dump in enumerate(probsup_dumps):
			for mac in mac_to_vector:
				if mac in probsup_dump:
					rssi = int(findall(r"%s, state: [0-9]+, cycle: [0-9]+, rssi: (-[0-9]+)" % mac, probsup_dump)[0])
					mac_to_vector[mac][idx] = rssi
				else:
					mac_to_vector[mac][idx] = 0
		return mac_to_vector

	def _locate(self, vector):
		if is_not_all_zeros(vector):
			remove_indexes = [idx for idx,rssi in enumerate(vector) if rssi == 0]
			vector = delete(vector, remove_indexes)
			distance_v = zeros(vector.shape[0])
			template_v = [[13.8, -70, 6], [1.5, -47, 1], [13.6, -73, -2]]
			for idx in range(vector.shape[0]):
				distance_v[idx] = template_v[idx][0] * 10 ** ((vector[idx] - (template_v[idx][1] - template_v[idx][2])) / 20)
			return distance_v.tolist()

	def _output_positioning_info(self, mac_to_vector, mac_to_position):
		info_table = Texttable()
		info_table.set_cols_align(["c"] * (3 + self._ap_amount))
		rows = [["MAC", "Name", "Position"] + ["RSSI from AP%s, dBm" % idx for idx in range(self._ap_amount)]]
		for mac,position in mac_to_position.items():
			rows.append([mac, self.mac_to_name[mac], position, *[rssi if rssi != 0 else None for rssi in mac_to_vector[mac]]])
		info_table.add_rows(rows)
		call(["clear"])
		print(info_table.draw())

	def run(self):
		resolution = [0, 0, ""]
		resolution[0] = 934
		resolution[1] = 312 + 30*len(self._clr_arr)
		resolution[2] = str(resolution[0]) + "x" + str(resolution[1])
		root = Tk()
		root.geometry(resolution[2])
		root.resizable(False, False)
		app = Window(root)

		while True:
			probsup_dumps = self._locator_queue.get()
			mac_to_vector = self._form_mac_to_vector_matchings(probsup_dumps)
			mac_to_position = {mac:self._locate(vector) for mac,vector in mac_to_vector.items()}

			resulting_position = list(mac_to_position.values())
			self._output_positioning_info(mac_to_vector, mac_to_position)
			Window.drawLater(app, resulting_position, self._clr_arr, resolution)

			root.update()
