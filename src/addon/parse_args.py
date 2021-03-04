from argparse import ArgumentParser

class ArgParser:
    def __init__(self):
        self._parser = ArgumentParser()
        self._def_args()

    def _def_args(self):
        self._parser.add_argument("-m", "--mode", action="store",\
                                type=str, dest="mode", required=True,\
                                default="L", help="Selects the positioning\
                                method from exisisting variants: Fingerprinting\
                                (F) / Lateration (L) / FTM (T).")


    def parse(self):
        cli_args = self._parser.parse_args()
        return cli_args
