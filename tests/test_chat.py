import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@patch("app.modules.brain.orchestrator.BrainOrchestrator.process_message", new_callable=AsyncMock)
def test_chat_endpoint(mock_process_message):
    mock_process_message.return_value = ("Hello from Brain!", "test-session-id")
    response = client.post("/api/v1/chat", json={"message": "Hi"})
    
    assert response.status_code == 200
    assert response.json() == {"response": "Hello from Brain!", "session_id": "test-session-id"}
