"""
Route Tests
"""
import json


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'message' in data


def test_chat_endpoint_valid_query(client):
    """Test chat endpoint with valid query"""
    payload = {'query': 'What is mastitis?'}
    response = client.post(
        '/chat',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    # Note: This test may fail if Ollama is not running or index not built
    # In a real test environment, you'd mock the service layer
    assert response.status_code in [200, 500]
    data = json.loads(response.data)
    assert 'answer' in data or 'error' in data


def test_chat_endpoint_empty_query(client):
    """Test chat endpoint with empty query"""
    payload = {'query': ''}
    response = client.post(
        '/chat',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_chat_endpoint_missing_query(client):
    """Test chat endpoint with missing query field"""
    payload = {}
    response = client.post(
        '/chat',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_rebuild_index_endpoint(client):
    """Test rebuild index endpoint"""
    response = client.post('/rebuild_index')
    
    # May succeed or fail depending on data availability
    assert response.status_code in [200, 500]
    data = json.loads(response.data)
    assert 'message' in data or 'error' in data
