# Quick experimental pyzmq pub/sub server.
# Code quality = not good
# Result of experiment = seems to work for our needs!

import zmq
import random
import time
import pickle

entity_size = 16
class Entity:
    def __init__(self):
        self.data = []
        for _ in range(1, entity_size):
            self.data.append(random.random() * 1e4930)

entities = []

def populate_entities():
    global entities
    entities = []
    for _ in range(1, 64):
        entities.append(Entity())
    # Client should check this
    entities[0].data[0] = 42

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:28430')

while True:
    populate_entities()
    print(len(pickle.dumps(entities))) # About 8 kb
    socket.send_string('space ' + pickle.dumps(entities))
    time.sleep(1)
