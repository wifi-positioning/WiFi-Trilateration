from os import access, R_OK
from os.path import isfile
from sys import exit
import json

class ConfigParser:

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

	def parse_config(self, config_file):
		raw_contents = self._load_contents(config_file)
		return self._decode_json(raw_contents)