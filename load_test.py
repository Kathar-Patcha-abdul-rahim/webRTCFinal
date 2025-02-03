import socketio
import time
import random

SERVER_URL = "http://localhost:5000"
NUM_CLIENTS = 10  # Increased for better load testing
TEST_CALLS = 5  # Number of test calls

clients = []

# Function to create a new client
def create_client(client_id):
    sio = socketio.Client()

    @sio.event
    def connect():
        print(f"Client {client_id} connected: {sio.sid}")

    @sio.event
    def offer(data):
        print(f"Client {client_id} received offer from {data['sender']}")
        # Send fake answer back
        sio.emit("answer", {"answer": "FAKE_ANSWER_SDP", "target": data["sender"]})
        print(f"Client {client_id} sent answer to {data['sender']}")
        # Send ICE candidate
        sio.emit("candidate", {"candidate": "FAKE_ICE_CANDIDATE", "target": data["sender"]})
        print(f"Client {client_id} sent ICE candidate to {data['sender']}")

    @sio.event
    def answer(data):
        print(f"Client {client_id} received answer from {data['sender']}")

    @sio.event
    def candidate(data):
        print(f"Client {client_id} received ICE candidate from {data['sender']}")

    @sio.event
    def disconnect():
        print(f"Client {client_id} disconnected: {sio.sid}")

    sio.connect(SERVER_URL)
    return sio

# Create clients with random delays
for i in range(NUM_CLIENTS):
    clients.append(create_client(i))
    time.sleep(random.uniform(0.2, 1))  # Simulating staggered client connections

print("All clients connected!")

# Set to keep track of clients that have already received offers in the current test
already_sent_to = set()

# Simulate sending random offers
for _ in range(TEST_CALLS):
    sender = random.choice(clients)  # Randomly select a sender
    # Randomly select a receiver, ensuring it is not the same as the sender and hasn't received an offer
    receiver_candidates = [c for c in clients if c != sender and c.sid not in already_sent_to]

    if receiver_candidates:
        receiver = random.choice(receiver_candidates)
        sender.emit("offer", {"offer": "FAKE_OFFER_SDP", "target": receiver.sid})
        print(f"Client {sender.sid} sent offer to {receiver.sid}")
        already_sent_to.add(receiver.sid)  # Mark this receiver as already sent to
    else:
        print(f"No available receiver for client {sender.sid}.")

time.sleep(10)  # Keep connections open for testing

# Disconnect all clients
for sio in clients:
    sio.disconnect()
