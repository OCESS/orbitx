import sys
import pickle
import zmq
import os
import time

topic = 'space'

class Entity:
    def __init__(self):
        self.data = []

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect ("tcp://corn-syrup.csclub.uwaterloo.ca:28430")
socket.setsockopt_string(zmq.SUBSCRIBE, topic)

# We'll wrie the second since starting this client that we received an update.
# Since the server sends an update every 1 second, with no congestion and in
# perfect network conditions we should see the heartbeat file have monotonically
# increasing integers, differing by one or two.
#
# I've tested this, with my setup being a laptop connected to wifi in the same
# city but a couple streets away from corn-syrup.csclub.uwaterloo.ca.
# The number of subclients seems to not affect how often updates are received.
# With one or thirty clients, the server publishes once a second and clients
# receive an update once a second.
#
# It seems that updates are lost only when the size of the update grows large.
# At <30 kb per update, all updates are received. As updates get larger, updates
# seem to take longer to send. This shouldn't matter, but the time between
# the client receiving an update and the size of an update seem to be linear.
# That is, as the size of the update grows linearly, a client will first get an
# update every couple seconds, then every five seconds, then every ten seconds.
# That part of the experiment wasn't important, so I didn't do any hard analysis
# on that.
#
# Suffice to say that it looks like pyzmq will be sufficient for our needs for
# networking!
start = time.monotonic()
heartbeat = open(str(os.getpid()), 'w')

while True:
    data = socket.recv()
    assert 42 == pickle.loads(data[len(topic)+1:])[0].data[0]
    print(int(time.monotonic() - start), file=heartbeat, flush=True)
