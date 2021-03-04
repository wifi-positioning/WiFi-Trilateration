from os import access, R_OK
from os.path import isfile
from numpy import genfromtxt
from sys import exit
import json

class CfgParser:
    def _load_contents(self, file_path):
        if isfile(file_path) and access(file_path, R_OK):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print("Can't load config file with path '%s'. Details: file does't exist or no permission to read it" % file_path)
            exit(1)

    def _decode_json(self, raw_contents):
        try:
            decoded_contents = json.loads(raw_contents)
        except json.decoder.JSONDecodeError as error:
            print("Can't parse config file. Details: %s" % error)
            exit(1)
        return decoded_contents

    def _add_radio_maps(self, decoded_contents):
        for ap in decoded_contents["ap_properties"]:
            try:
                ap["radio_map"] = genfromtxt(ap["radio_map"], delimiter=",")
            except OSError as error:
                print("Can't load radio map file with path '%s'. Details: %s" % (ap["radio_map"], error))
                exit(1)

    def parse(self, cli_args):
        config_file = "data/config/config.json"
        raw_contents = self._load_contents(config_file)
        decoded_contents = self._decode_json(raw_contents)
        self._add_radio_maps(decoded_contents)
        mode = {"mode" : cli_args.mode}
        decoded_contents.update(mode)
        return decoded_contents
