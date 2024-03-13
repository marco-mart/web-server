from queue import Queue, Empty
import socket
from threading import Event, Thread
from time import sleep
from logging_config.logger_tools import get_logger
from typing import Tuple
from enum import StrEnum

logger = get_logger()


class HttpMethods(StrEnum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class RequestProcessor(Thread):
    
    """
    This class acts as the request routing system.
    It extends the Thread class and will attempt to
    retrieve from the request queue for the it's 
    entire lifespan until death.
    """
    
    _request_queue: Queue        = None
    _die: Event                  = None
    _connection: socket.socket   = None
    _ip_address: str             = None


    def __init__(self, die: Event, request_queue: Queue[Tuple[socket.socket, Tuple[str, int]]]) -> None:
        Thread.__init__(self)
        self._request_queue = request_queue
        self._die = die        
    
    def run(self) -> None:

        while not self._die.is_set():
            
            try:
                _req = self._request_queue.get_nowait()
                self.route_request((_req[0], _req[1]))
                
            except Empty:
                sleep(1)
                continue
    
    def route_request(self, request: Tuple[socket.socket, Tuple[str, int]]) -> None:

        """
        Reads the request's request line, and routes the
        request based on it's HTTP method.
        """

        self._connection = request[0]
        self._ip_address = request[1]

        buff = self._connection.recv(4096)
        if buff is None:
            logger.error('Client disconnected!!')
        
        _req_headers, _req_body = buff.decode(encoding='utf-8').split("\r\n\r\n")
                
        _req_header_lines = _req_headers.split('\r\n')

        if len(_req_header_lines) < 2:
            logger.error('HTTP request is malformed! From ip: %s', self._ip_address)
            return
        

        _req_line = _req_header_lines[0]

        _http_method, _request_uri, _http_version = _req_line.split(' ')

        if any(x is None for x in [_http_method, _request_uri, _http_version]):
            logger.error('HTTP request is malformed!')
            return
        
        # TODO: REROUTE FOR HTTP 2.0
        
        # At this point we have only read 4096 bytes.
        # Make sure to handle the case where the requests
        # are longer.
        if _http_method == HttpMethods.GET:
            self.process_get_request(_request_uri, _req_header_lines, _req_body)
        elif _http_method == HttpMethods.POST:
            pass
        elif _http_method == HttpMethods.PUT:
            pass
        elif _http_method == HttpMethods.DELETE:
            pass

    def process_get_request(self, uri: str, req_headers: list[str], _req_body: str):
        """
        Process HTTP GET requests.
        """
        # Prepare the HTTP response
        http_response = (
            'HTTP/1.1 200 OK\r\n'
            'Date: Mon, 27 Jul 2009 12:28:53 GMT\r\n'
            'Server: Apache/2.2.14 (Win32)\r\n'
            'Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT\r\n'
            'Content-Type: text/html\r\n'
            '\r\n'
            '<!DOCTYPE html><html><body><h1>Hello, World!</h1></body></html>'
        )
        # Calculate the correct content length
        content_length = len(http_response.encode('utf-8'))
        # Add the content length to the headers
        http_response = http_response.replace('Content-Type: text/html\r\n', f'Content-Length: {content_length}\r\nContent-Type: text/html\r\n')
        
        # Send the response
        self._connection.sendall(http_response.encode('utf-8'))
        self._connection.close()

    def process_post_request():
        pass

    def process_put_request():
        pass

    def process_delete_request():
        pass
    
