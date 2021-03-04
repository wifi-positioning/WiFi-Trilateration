from numpy import zeros, delete, unravel_index, any as is_not_all_zeros
from collections import OrderedDict
from subprocess import call
from re import findall
import csv

class DumpParser:
    def dump_parser(self, config, probsup_dumps):
        get_rssi = 0
        mac_to_vector = {mac:zeros(config._radio_map.shape[0]) for mac in config.mac_to_name}
        for idx,probsup_dump in enumerate(probsup_dumps):
            if probsup_dump[0] == 0:
                for mac in mac_to_vector:
                    if mac in probsup_dump[1]:
                        rssi_tmp = findall(r"%s, state: [0-9]+, cycle: [0-9]+, rssi: (-[0-9]+)" % mac, probsup_dump[1])
                        if len(rssi_tmp) > 0:
                            mac_to_vector[mac][idx] = int(rssi_tmp[0])
                    else:
                        mac_to_vector[mac][idx] = 0
            elif probsup_dump[0] == 1:
                for iter in probsup_dump[1]:
                    raw_data = iter.split("|")
                    if len(raw_data) > 1:
                        if raw_data[0].strip() == "hw-addr":
                            mac = raw_data[1].strip()
                            if mac in config.mac_to_name:
                                get_rssi = 1
                            else:
                                get_rssi = 0
                        if raw_data[0].strip() == "rssi-1" and get_rssi == 1:
                            rssi_tmp = raw_data[1].strip()
                            if len(rssi_tmp) > 0:
                                mac_to_vector[mac][idx] = int(rssi_tmp)
                                get_rssi = 0
        sorted_list = self.best_rssi(config, mac_to_vector)
        return sorted_list

    def best_rssi(self, config, mac_to_vector):
        base_vector = {ap_num : 0 for ap_num in range(config._ap_amount)}
        mac_vector = {mac: [0] for mac in config.mac_to_name}
        for mac,vector in mac_to_vector.items():
            iter = 0
            viter = 0
            # for rssi in vector:
            #     if rssi == 0:
            #         base_vector[iter] = -200
            #         iter += 1
            #     else:
            #         base_vector[iter] = int(rssi)
            #         iter += 1
            base_vector[0] = int(-66.5)
            base_vector[1] = int(-64)
            base_vector[2] = int(-39)
            sorted_vector = sorted(base_vector.items(), key=lambda x: x[1], reverse=True)
            mac_vector[mac][viter] = sorted_vector
            viter += 1
        return mac_vector

    def parse(self, config, probsup_dumps):
        data = self.dump_parser(config, probsup_dumps)
        return data
