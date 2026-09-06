import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock, MagicMock

client = TestClient(app)

@patch("app.modules.sessions.service.SessionService.list_sessions", new_callable=AsyncMock)
def test_list_sessions(mock_list):
    mock_list.return_value = []
    response = client.get("/api/v1/sessions")
    
    assert response.status_code == 200
    assert response.json() == []
    mock_list.assert_called_once()
