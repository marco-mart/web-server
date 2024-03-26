from time import sleep
from connection_handler import ConnectionHandler
from threading import Event
from queue import Queue
import requests
import unittest
# Unit tests for connection_handler.py.

class TestConnectionHandler(unittest.TestCase):

    def test_queue_content(self):
        address = 'http://localhost:8080/'
        die = Event()
        q = Queue()
        ch = ConnectionHandler(die, q)
        
        # Start thread.
        ch.start()
        sleep(3)
        print('Thread is running.')
        r = requests.get(address)

        print('Sent request.')
        
        # Grab first queue object.
        first_item = q.get_nowait() 
        self.assertEqual(first_item[1], '127.0.0.1')

        # Kill thread.
        die.set()


if __name__ == '__main__':
    unittest.main()