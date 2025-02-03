import pytest
from flask_socketio import SocketIOTestClient
from app import app, socketio


@pytest.fixture
def test_client():
    return socketio.test_client(app)


def get_sid(client: SocketIOTestClient):
    """Retrieve the SID from the server response."""
    client.get_received()  # Clear any previous messages
    client.emit("connect")  # Trigger connection
    messages = client.get_received()

    for msg in messages:
        if msg["name"] == "sid":
            return msg["args"][0]["sid"]

    return None  # If SID is not found


def test_offer_event(test_client: SocketIOTestClient):
    recipient_client = socketio.test_client(app)
    recipient_sid = get_sid(recipient_client)

    assert recipient_sid is not None, "Recipient SID could not be retrieved"

    test_client.emit("offer", {"offer": "test-offer", "target": recipient_sid})
    received = recipient_client.get_received()

    assert any(event["name"] == "offer" for event in received), "Offer event was not received"


def test_answer_event(test_client: SocketIOTestClient):
    recipient_client = socketio.test_client(app)
    recipient_sid = get_sid(recipient_client)

    assert recipient_sid is not None, "Recipient SID could not be retrieved"

    test_client.emit("answer", {"answer": "test-answer", "target": recipient_sid})
    received = recipient_client.get_received()

    assert any(event["name"] == "answer" for event in received), "Answer event was not received"


def test_candidate_event(test_client: SocketIOTestClient):
    recipient_client = socketio.test_client(app)
    recipient_sid = get_sid(recipient_client)

    assert recipient_sid is not None, "Recipient SID could not be retrieved"

    test_client.emit("candidate", {"candidate": "test-candidate", "target": recipient_sid})
    received = recipient_client.get_received()

    assert any(event["name"] == "candidate" for event in received), "Candidate event was not received"
