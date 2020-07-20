from argparse import ArgumentParser, FileType
import signal
import sys
# import threading
import multiprocessing
from .client import Client
from .utils.logger import log
from .utils.utils import load_config


def main():
    _do_main()
    # try:

    # except Exception as err:
    #     log.fatal(err)
    #     sys.exit(1)


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


def start_client(cfg, node):
    # TODO FIX
    # try:
    client = Client(common=cfg.common,
                    consensus_constants=cfg.consensus_constants, node=node)
    clients.append(client)
    client.run_client()
    # except Exception as e:
    #     print("Exception", e)


def interruptHandler(sig, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(sig))
    # https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32
    for client in clients:
        client.close()
    # https://stackoverflow.com/questions/27751198/what-is-the-difference-between-next-and-until-in-pdb
    # https://www.digitalocean.com/community/tutorials/how-to-use-the-python-debugger
    # until, next and step
    # import pdb
    # pdb.Pdb().set_trace(frame)
    #     jobs.append(
    #         asyncio.ensure_future(client.close()))
    # loop.run_until_complete(asyncio.gather(*jobs))


signal.signal(signal.SIGINT, interruptHandler)


def start(args):
    args.config = load_config(args.config)
    threads = []
    # number_of_p = len(args.config.nodes)

    # due to fork safety in mac os
    # Error:
    # may have been in progress in another thread when fork() was called.
    # We cannot safely call it or ignore it in the fork() child process.
    # Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.

    # https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_multiprocessing.htm
    # https://stackoverflow.com/questions/3033952/threading-pool-similar-to-the-multiprocessing-pool
    # prevention
    # export  OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

    for node in args.config.nodes:
        threads.append(multiprocessing.Process(
            # threads.append(threading.Thread(
            target=start_client, args=(args.config, node)))
    for thread in threads:
        thread.start()
        # by setting deamon True on the exit of main process
        # subprocess will be killed
        thread.deamon = True
    for thread in threads:
        thread.join()
    log.info("Exit All!!")
    sys.exit(0)


if __name__ == "__main__":
    main()
