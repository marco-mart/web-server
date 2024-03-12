"""
web_server_starter.py
Start's a web server by:
- creating an atomic boolean that ensures the graceful
  death of the server
- creating a thread-safe queue that the requests are placed in.
- initializing request processor thread
- initializing  the request processors
"""

from queue import Queue
from threading import Event, Thread
import threading
from time import sleep
from web_server.components.connection_handler import ConnectionHandler
from typing import List
from logging_config.logger_tools import get_logger

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

def start_threads() -> None:
    """
    Start connection handler thread.
    """
    ch = ConnectionHandler(_die, _request_queue)
    _threads.append(ch)
    ch.start()
    logger.info('Started ConnectionHandler thread!')

def main():
    """
    Web server entry point.
    """
    global _request_queue
    global _die
    global _threads

    _request_queue = Queue()
    _die = Event()
    _threads = []

    start_threads()

    print("Enter 'die' to kill the server.")
    while not _die.is_set():

        _request_queue.put_nowait('bruh')
        
        if input() == 'die':
            _die.set()
            break
        print(f'{threading.active_count()=}')


    exit_gracefully()

if __name__ == '__main__':
    main()