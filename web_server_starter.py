'''
web_server_starter.py
Start's a web server by:
- creating an atomic boolean that ensures the graceful
  death of the server
- creating a thread-safe queue that the requests are placed in.
- initializing request processor thread
- initializing  the request processors
'''

from queue import Queue
from threading import Event

# Web server singletons.
_request_queue: Queue = None
_die: Event = None

def exit_gracefully() -> None:
    print('web_server_starter thread is dead!')

def start_threads() -> bool: 
    return True

def main():
    '''
    Web server entry point.
    '''

    _request_queue = Queue()
    _die = Event()

    if not start_threads():
        print('Failed to start web server!')
    else:
        print('Starting web server!')

    print("Enter 'die' to kill the server.")
    while not _die.is_set():
        
        user_input = input()
        if user_input == 'die':
            _die.set()
            exit_gracefully()

    

if __name__ == '__main__':
    main()