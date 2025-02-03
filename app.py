from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins

connections = {}

@socketio.on("connect")
def on_connect():
    emit("sid", {"sid": request.sid})  # Send SID back to client
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def on_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in connections:
        del connections[request.sid]

@socketio.on("offer")
def on_offer(data):
    print(f"Received offer from {request.sid}, sending to {data['target']}")
    emit("offer", {"offer": data["offer"], "sender": request.sid}, room=data["target"])

@socketio.on("answer")
def on_answer(data):
    print(f"Received answer from {request.sid}, sending to {data['target']}")
    emit("answer", {"answer": data["answer"], "sender": request.sid}, room=data["target"])

@socketio.on("candidate")
def on_candidate(data):
    print(f"Received ICE candidate from {request.sid}, sending to {data['target']}")
    emit("candidate", {"candidate": data["candidate"], "sender": request.sid}, room=data["target"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
