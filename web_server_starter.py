"""
Start's web server on localhost port 8080
"""

from enum import StrEnum, IntEnum
from queue import Queue
from threading import Event, Thread, active_count
from web_server.components.connection_handler import ConnectionHandler
from web_server.components.request_processor import RequestProcessor
from logging_config.logger_tools import get_logger

class ServerIpAddress(StrEnum):
    IP_ADDRESS = '127.0.0.1'

class ServerPort(IntEnum):
    PORT = 8080

# Grab logger instance.
logger = get_logger()

# Web server singletons.
_request_queue: Queue = None
_die: Event = None
_threads: list[Thread] = None

def exit_gracefully() -> None:
    """
    Kill server gracefully.
    """
    for t in _threads:
        t.join()
    logger.info('web_server_starter thread is dead!')

def start_connection_handler_thread() -> None:
    """
    Start connection handler thread.
    """
    ch = ConnectionHandler(_die, _request_queue,
                           ServerIpAddress.IP_ADDRESS,
                           ServerPort.PORT)
    _threads.append(ch)
    ch.start()
    logger.info('Started ConnectionHandler thread!')

def start_request_processor_threads():
    """
    Start request processor threads.
    """
    # TODO: Calculate the number of CPU cores, give each a thread.
    rp = RequestProcessor(_die, _request_queue)
    _threads.append(rp)
    rp.start()
    logger.info('Started RequestProcessor thread!')

def main() -> None:
    """
    Web server entry point.
    """
    global _request_queue
    global _die
    global _threads

    _request_queue = Queue()
    _die = Event()
    _threads = []

    start_connection_handler_thread()
    start_request_processor_threads()
    logger.info('Active threads: %s', active_count())

    print("Enter 'die' to kill the server.")
    while not _die.is_set():
        
        if input() == 'die':
            _die.set()
            break

    exit_gracefully()

if __name__ == '__main__':
    main()