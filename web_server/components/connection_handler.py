from threading import Thread, Event
from queue import Empty, Queue
import socket
from time import sleep
from logging_config.logger_tools import get_logger
# from components.definitions import connection as connection


"""
The purpose of this class is to listen for requests
at the port and ip address specified in it's init.

It acts as a Producer for the RequestProcessor class
by placing the incoming connections in the queue for
processing.
"""

logger = get_logger()

class ConnectionHandler(Thread):

    _request_queue: Queue  = None
    _die: Event            = None
    _ip_address: str       = '127.0.0.1'
    _port_number: int      = 8080

    def __init__(self, die: Event, queue: Queue) -> None:
        """
        Init.
        """
        Thread.__init__(self)
        # Thread.__init__(self)
        self._die = die
        self._request_queue = queue
        logger.info('Initialized ConnectionHandler!')
    
    def exit_gracefully(self):
        """
        Not to sure what to put in here.
        """
        logger.info('ConnectionHandler died gracefully!')

    def run(self):
        """
        Grab connections and place them in the queue for processing.
        """
        logger.info('Inside run method.')
        while not self._die.is_set():
            try:
                print(self._request_queue.get_nowait())
            except Empty:
                continue
        self.exit_gracefully()
        # print('Inside run\n')

        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #     sock.bind((self._ip_address, self.port))
        #     sock.listen()
        #     # Allow socket to be reused for many different connections.
        #     # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #     print('Bind to port 8080, listening...\n')

        #     # while not self._die.is_set():
        #     conn, addr = sock.accept()
        #     with conn:
        #         print('Accepted connection from: \n', addr)
        #         self._request_queue.put_nowait((conn, addr))
                
        #         # Prepare the HTTP response
        #         http_response = (
        #             'HTTP/1.1 200 OK\r\n'
        #             'Date: Mon, 27 Jul 2009 12:28:53 GMT\r\n'
        #             'Server: Apache/2.2.14 (Win32)\r\n'
        #             'Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT\r\n'
        #             'Content-Type: text/html\r\n'
        #             'Connection: close\r\n'
        #             '\r\n'
        #             '<html><body><h1>Hello, World!</h1></body></html>'
        #         )
        #         # Calculate the correct content length
        #         content_length = len(http_response.encode('utf-8'))
        #         # Add the content length to the headers
        #         http_response = http_response.replace('Content-Type: text/html\r\n', f'Content-Length: {content_length}\r\nContent-Type: text/html\r\n')
                
        #         # Send the response
        #         conn.sendall(http_response.encode('utf-8'))
        #         conn.close()



