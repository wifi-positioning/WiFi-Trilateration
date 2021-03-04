#!/usr/bin/env python3
global srv_engine

def sig_handler(signal, frame):
    global srv_engine
    srv_engine.shutdown()
    exit(1)

def main():
    global srv_engine
    signal(SIGINT, sig_handler)
    cli_args = ArgParser().parse()
    load_config = CfgParser().parse(cli_args)
    print("[ TESTING PROJECT ]\nPosition's pattern:\n\t=> Relative:\t2 x 3\n\t=> Absolute:\t8.6 x 22.8\n\n")
    srv_engine = Engine(load_config)
    srv_engine.run()


if __name__ == '__main__':
    try:
        from addon.parse_args import ArgParser
        from addon.parse_config import CfgParser
        from sys import exit
        from engine import Engine
        from signal import signal, SIGINT
    except Exception as e:
        print(e)
        exit(1)
    main()
