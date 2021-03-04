from multiprocessing import Process
from gui.finger_ui import gui
from addon.parse_dumps import DumpParser
# from gui.later_ui import Later_UI
from numpy import zeros, delete, unravel_index, any as is_not_all_zeros
from numpy import log10, linalg
from texttable import Texttable
from subprocess import call
from re import findall
from math import sqrt
from tkinter import *
import csv

global resulting_position
class Locator(Process):
    def __init__(self, locator_queue, config):
        super().__init__()
        self._mode = config["mode"]
        self._ap_list = config["ap_properties"]
        self._ap_amount = len(config["ap_properties"])
        self._locator_queue = locator_queue
        self._radio_map = self._form_radio_map(config["ap_properties"])
        self.mac_to_name = config["monitoring_properties"]["users"]
        self._ap_cords = [[0, 0, 0] for ap in range(self._ap_amount)]
        self._ap_freq = [0 for ap in range(self._ap_amount)]
        self._ap_txp = [0 for ap in range(self._ap_amount)]
        for ap in range(len(self._ap_freq)):
            self._ap_freq[ap] = int(self._ap_list[ap]["frequency"])
        for ap in range(len(self._ap_freq)):
            self._ap_txp[ap] = float(self._ap_list[ap]["tx-p"])
        for ap in range(len(self._ap_cords)):
            raw_cords = self._ap_list[ap]["ap_cords"].split(";")
            for cords in range(len(raw_cords)):
                self._ap_cords[ap][cords] = float(raw_cords[cords])

    def _form_radio_map(self, ap_properties):
        radio_map = zeros((len(ap_properties), *ap_properties[0]["radio_map"].shape))
        for idx,ap in enumerate(ap_properties):
            radio_map[idx] = ap["radio_map"]
        return radio_map

    def _locate(self, vector):
        def obs_cnt(sWall_n, lWall_n):
            obs_loss = sWall_n*3.4+lWall_n*6.9
            return obs_loss
        top_vector = [vector[0][1], vector[1][1], vector[2][1]]
        dist_vector = [0,0,0]
        if is_not_all_zeros(top_vector):
            print("RSSI - Distance:")
            for idx in range(len(top_vector)):
                if top_vector[idx] > -40:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+6-32.45-10)/20)*1000
                elif top_vector[idx] > -50 and top_vector[idx] <= -40:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+15-32.45-obs_cnt(2,1))/20)*1000
                elif top_vector[idx] > -60 and top_vector[idx] <= -50:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+15-32.45-obs_cnt(2,2))/20)*1000
                elif top_vector[idx] > -70 and top_vector[idx] <= -60:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+15-32.45-obs_cnt(3,3))/20)*1000
                elif top_vector[idx] > -80 and top_vector[idx] <= -70:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+15-32.45-obs_cnt(2,4))/20)*1000
                elif top_vector[idx] <= -80:
                    dist_vector[idx] = 10 ** ((-top_vector[idx]+self._ap_txp[idx]-(-5)-20*log10(self._ap_freq[idx])+15-32.45-obs_cnt(3,4))/20)*1000
                print(top_vector[idx]," - ",dist_vector[idx], "|", self._ap_freq[idx],"-",self._ap_txp[idx])
            print()
            return dist_vector

    def _pos_calc(self, cords, vec):
        # if self._cords_check(cords, vec):
        #     x = (cords[1][0]**2+vec[0]**2-vec[1]**2)/(2*cords[1][0])
        #     y = (cords[2][0]**2+cords[2][1]**2+vec[0]**2-vec[2]**2-2*cords[2][0]*x)/(2*cords[2][1])
        #     z = sqrt(abs(vec[0]**2-x**2-y**2))
        # x = ((cords[1][1]-cords[0][1])*(vec[1]**2-vec[2]**2-cords[1][1]**2+cords[2][1]**2-cords[1][0]**2+cords[2][0]**2)-\
        #     (cords[2][1]-cords[1][1])*(vec[0]**2-vec[1]**2-cords[0][1]**2+cords[1][1]**2-cords[0][0]**2+cords[1][0]))/\
        #     (2*((cords[2][1]-cords[1][1])*(cords[0][0]-cords[1][0])-(cords[1][1]-cords[0][1])*(cords[1][0]-cords[2][0])))
        # y = ((cords[1][0]-cords[0][0])*(vec[1]**2-vec[2]**2-cords[1][0]**2+cords[2][0]**2-cords[1][1]**2+cords[2][1]**2)-\
        #     (cords[2][0]-cords[1][0])*(vec[0]**2-vec[1]**2-cords[0][0]**2+cords[1][0]**2-cords[0][1]**2+cords[1][1]))/\
        #     (2*((cords[2][0]-cords[1][0])*(cords[0][1]-cords[1][1])-(cords[1][0]-cords[0][0])*(cords[1][1]-cords[2][1])))
        # print(x,y)
        # if (abs((cords[1][0]-x)**2+(cords[1][1]-y)**2-vec[0]**2)<0.000001):
        #     return round(x,1),round(y,1),1
        return -1

    def _cords_check(self, cords, vec):
        def cond_v(cords, vec, i, j):
            dist = sqrt((cords[i][0]-cords[j][0])**2+(cords[i][1]-cords[j][1])**2)
            return (abs(vec[i]-vec[j]) <= dist) and (dist <= vec[i] + vec[j])
        return cond_v(cords, vec, 0, 1) and cond_v(cords, vec, 0, 2) and cond_v(cords, vec, 1, 2)

    def _data_export(self, mac_to_vector, mac_to_position):
        iter_mac = 0
        iter_rssi = 0
        rssi_fin = [[0.0 for cnt in range (self._ap_amount)] for cnt in range(len(self.mac_to_name))]
        for mac,position in mac_to_position.items():
            iter_rssi = 0
            for rssi in mac_to_vector[mac]:
                if rssi == 0:
                    rssi_fin[iter_mac][iter_rssi] = None
                else:
                    rssi_fin[iter_mac][iter_rssi] = rssi
                iter_rssi+=1
            iter_mac+=1
        iter_mac = 0
        with open('data/logs/radio_map.csv', 'a+', newline='') as f:
            writer = csv.writer(f)
            for mac,position in mac_to_position.items():
                writer.writerow([mac, self.mac_to_name[mac], rssi_fin[iter_mac]])
                iter_mac += 1

    def _output_positioning_info(self, mac_to_vector, res_pos, mac_to_position):
        info_table = Texttable()
        info_table.set_cols_align(["c"] * (3 + self._radio_map.shape[0]))
        info_table.set_cols_width([18] * (3 + self._radio_map.shape[0]))
        rows = [["MAC", "Name", "Position"] + ["Distance between Top-%s AP and Agent, m" % int(idx+1) for idx in range(self._radio_map.shape[0])]]
        for mac in mac_to_position:
            rows.append([mac, self.mac_to_name[mac],*[[cords for cords in res_pos[mac]] if res_pos[mac] != -1 else "N/A"],*[dist for dist in mac_to_position[mac]]])
            info_table.add_rows(rows, header=True)
        call(["clear"])
        print(info_table.draw())

    def run(self):
        # pass
        # root = Tk()
        # root.geometry("1200x1023")
        # root.resizable(False, False)
        # app = Later_UI(root)
        while True:
            probsup_dumps = self._locator_queue.get()
            mac_to_vector = DumpParser().parse(self, probsup_dumps)
            mac_to_position = {mac:self._locate(vector[0]) for mac,vector in mac_to_vector.items()}
            res_position = {mac:self._pos_calc(self._ap_cords, vector) for mac,vector in mac_to_position.items()}
            # self._output_positioning_info(mac_to_vector, res_position, mac_to_position)
            for mac,rssi in mac_to_vector.items():
                rssi_vec = [rssi[0][0][1], rssi[0][1][1], rssi[0][2][1]]
            print(res_position)
            # Later_UI.drawPos(app, rssi_vec, mac_to_position)
            # root.update()
