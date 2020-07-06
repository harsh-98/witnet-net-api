import threading
import sys
from .utils.logger import log
import toml
from argparse import ArgumentParser, FileType
from witnet_lib.utils import AttrDict
from .client import Client
import signal


def main():
    try:
        _do_main()
    except Exception as err:
        log.fatal(err)
        sys.exit(1)


def _do_main():
    parser = setup_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


def setup_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.add_argument('-v', '--version', action='version',
                        version=f"erdpy ")
    parser.add_argument('--verbose', action='store_true',
                        default=False)

    sub = subparsers.add_parser("run")
    sub.add_argument("-c", "--config", type=FileType('r'), required=False,
                     default="api.toml")
    sub.set_defaults(func=start)
    return parser


clients = []


def start_client(web_addr, node):
    try:
        client = Client(web_addr=web_addr, node=node)
        clients.append(client)
        client.run_client()
    except Exception as e:
        print("Exception", e)


def interruptHandler(sig, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(sig))
    # https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32
    for client in clients:
        client.close()
    import sys
    sys.exit(0)


signal.signal(signal.SIGINT, interruptHandler)


def start(args):
    config = toml.load(args.config)
    args.config = AttrDict(**config)

    threads = []
    for node in args.config.nodes:
        threads.append(threading.Thread(
            target=start_client, args=(args.config.web_addr, AttrDict(**node))))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
