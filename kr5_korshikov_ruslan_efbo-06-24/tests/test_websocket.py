import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_websocket_connect_success():
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "system"
        assert "alice joined" in msg["message"]

def test_websocket_missing_username():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/test") as ws:
            pass

def test_send_and_receive_message():
    with client.websocket_connect("/ws/rooms/room1?username=bob") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "text": "Hello everyone"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["text"] == "Hello everyone"
        assert msg["username"] == "bob"

def test_two_clients_same_room():
    with client.websocket_connect("/ws/rooms/room2?username=alice") as ws1:
        ws1.receive_json()
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            ws2.receive_json()
            ws1.receive_json()
            ws1.send_json({"type": "message", "text": "Hi bob"})
            msg_bob = ws2.receive_json()
            assert msg_bob["type"] == "message"
            assert msg_bob["text"] == "Hi bob"
            msg_alice = ws1.receive_json()
            assert msg_alice["type"] == "message"
            assert msg_alice["text"] == "Hi bob"

def test_different_rooms_isolated():
    with client.websocket_connect("/ws/rooms/roomA?username=alice") as wsA:
        wsA.receive_json()
        with client.websocket_connect("/ws/rooms/roomB?username=bob") as wsB:
            wsB.receive_json()
            wsA.send_json({"type": "message", "text": "secret"})
            msgA = wsA.receive_json()
            assert msgA["text"] == "secret"

def test_message_too_long():
    with client.websocket_connect("/ws/rooms/roomL?username=alice") as ws:
        ws.receive_json()
        long_text = "x" * 301
        ws.send_json({"type": "message", "text": long_text})
        error_msg = ws.receive_json()
        assert error_msg["type"] == "error"
        assert "too long" in error_msg["detail"]

def test_user_removed_after_disconnect():
    with client.websocket_connect("/ws/rooms/roomX?username=alice") as ws:
        ws.receive_json()
        resp = client.get("/rooms/roomX/users")
        assert resp.json()["users"] == ["alice"]
    resp = client.get("/rooms/roomX/users")
    assert resp.json()["users"] == []