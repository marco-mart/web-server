# Named tuple data structure used inside of request queue.
from collections import namedtuple
Connection = namedtuple("connection", ["conn", "addr"])