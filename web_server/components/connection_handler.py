from threading import Thread, Event
from queue import Empty, Queue
import socket
from time import sleep
from logging_config.logger_tools import get_logger


logger = get_logger()

class ConnectionHandler(Thread):
    """
    The purpose of this class is to listen for requests
    at the port and ip address specified in it's init.

    It acts as a Producer for the RequestProcessor class
    by placing the incoming connections in the queue for
    processing.
    """

    _request_queue: Queue  = None
    _die: Event            = None
    _ip_address: str       = None
    _port_number: int      = None

    def __init__(self, die: Event, queue: Queue,
                 ip_address: str, port_number: int) -> None:
        """
        Init.
        """
        Thread.__init__(self)
        # Thread.__init__(self)
        self._die = die
        self._request_queue = queue
        self._ip_address = ip_address
        self._port_number = port_number
        logger.info('Initialized ConnectionHandler!')
    
    def exit_gracefully(self) -> None:
        """
        Not to sure what to put in here.
        """
        logger.info('ConnectionHandler died gracefully!')

    def run(self) -> None:
        """
        Grab connections and place them in the queue for processing.
        """
        logger.debug('Inside run method.')

        # 'with' keyword closes the connection as soon as it's done.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow socket to be reused for different connections.
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._ip_address, self._port_number))
        sock.listen()

        logger.info('Finished binding to port 8080. Listening...')

        while not self._die.is_set():
            conn, addr = sock.accept()
            logger.info('Accepted connection from: %s\n', addr)
            self._request_queue.put_nowait((conn, addr))

        self.exit_gracefully()




