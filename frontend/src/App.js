import React, { useRef, useState, useEffect } from "react";
import io from "socket.io-client";
import './App.css'

const socket = io("http://localhost:5000"); // Connect to Flask WebSocket server

const App = () => {
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);
    const peerConnectionRef = useRef(null);
    const [userId, setUserId] = useState(null);
    const [partnerId, setPartnerId] = useState("");

    useEffect(() => {
        socket.on("connect", () => {
            console.log("Connected to signaling server");
            setUserId(socket.id);
        });

        socket.on("offer", async ({ offer, sender }) => {
            console.log("Received offer:", offer);
            peerConnectionRef.current = createPeerConnection(sender);

            await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await peerConnectionRef.current.createAnswer();
            await peerConnectionRef.current.setLocalDescription(answer);

            socket.emit("answer", { answer, target: sender });
            console.log("Sent answer to", sender);
        });

        socket.on("answer", async ({ answer }) => {
            console.log("Received answer:", answer);
            await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(answer));
        });

        socket.on("candidate", async ({ candidate }) => {
            console.log("Received ICE candidate:", candidate);
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
        });

        return () => {
            socket.off("offer");
            socket.off("answer");
            socket.off("candidate");
        };
    }, []);

    const startCall = async () => {
        peerConnectionRef.current = createPeerConnection(partnerId);

        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideoRef.current.srcObject = stream;

        stream.getTracks().forEach((track) => peerConnectionRef.current.addTrack(track, stream));

        const offer = await peerConnectionRef.current.createOffer();
        await peerConnectionRef.current.setLocalDescription(offer);

        socket.emit("offer", { offer, target: partnerId });
        console.log("Sent offer to", partnerId);
    };

    const createPeerConnection = (partnerId) => {
        const pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
        });

        pc.onicecandidate = (event) => {
            if (event.candidate) {
                console.log("Sending ICE candidate:", event.candidate);
                socket.emit("candidate", { candidate: event.candidate, target: partnerId });
            }
        };

        pc.ontrack = (event) => {
            console.log("Received track:", event.streams[0]);
            if (remoteVideoRef.current) {
                remoteVideoRef.current.srcObject = event.streams[0];
            }
        };

        return pc;
    };

    return (
        <div>
            <h1>WebRTC Video Call</h1>
            <div>
                <h2>Your ID: {userId}</h2>
                <input
                    type="text"
                    placeholder="Enter partner ID"
                    value={partnerId}
                    onChange={(e) => setPartnerId(e.target.value)}
                />
                <button onClick={startCall}>Start Call</button>
            </div>
            <div style={{ display: "flex" }}>
                <video ref={localVideoRef} autoPlay playsInline muted style={{ width: "45%", margin: "5px" }} />
                <video ref={remoteVideoRef} autoPlay playsInline style={{ width: "45%", margin: "5px" }} />
            </div>
        </div>
    );
};

export default App;
