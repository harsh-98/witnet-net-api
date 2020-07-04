import threading
import sys
from argparse import ArgumentParser
from witnet_lib.utils import AttrDict
import logging

from .client import Client
# from witnet_api import __version__
logger = logging.getLogger("api")


def main():
    try:
        _do_main()
    except Exception as err:
        logger.fatal(err)
        sys.exit(1)


def _do_main():
    parser = setup_parser()
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    else:
        logging.basicConfig(level=logging.WARN)

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
    sub.add_argument("--ws", type=str, required=False,
                     default="http://localhost:3000")
    sub.set_defaults(func=start)
    return parser


def start_client(args, node_addr):
    Client(node_id=node_addr, node_addr=node_addr,
           ws=args.ws).run_client()


def start(args):
    # threads = []
    # ['127.0.0.1:21337', '127.0.0.1:21339', '127.0.0.1:21341', '127.0.0.1:21343', '127.0.0.1:21345',
    #    '127.0.0.1:21347', '127.0.0.1:21349', '127.0.0.1:21351', '127.0.0.1:21353', '127.0.0.1:21355']
    # for node_addr in ['127.0.0.1:21337', '127.0.0.1:21339']:
    #     threads.append(threading.Thread(
    #         target=start_client, args=(args, node_addr)))
    # for thread in threads:
    #     thread.start()
    # for thread in threads:
    #     thread.join()
    node_addr = "127.0.0.1:21337"
    Client(node_id=node_addr, node_addr=node_addr,
           ws=args.ws).run_client()


if __name__ == "__main__":
    main()
