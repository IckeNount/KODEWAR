import pytest
from django.test import Client
from django.urls import reverse
import json
import uuid

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def auth_headers():
    # TODO: Replace with actual authentication token
    return {'HTTP_AUTHORIZATION': 'Bearer test-token'}

def test_submission_endpoint_health(client, auth_headers):
    """Test that the submission endpoint is accessible."""
    response = client.get(reverse('code-submission'), **auth_headers)
    assert response.status_code == 405  # Method not allowed for GET

def test_status_endpoint_health(client, auth_headers):
    """Test that the status endpoint is accessible."""
    response = client.get(reverse('submission-status'), **auth_headers)
    assert response.status_code == 400  # Bad request due to missing submission_id

def test_submission_validation(client, auth_headers):
    """Test submission validation."""
    # Test missing required fields
    response = client.post(
        reverse('code-submission'),
        data=json.dumps({}),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 400
    assert 'code' in response.json()
    assert 'language' in response.json()

    # Test invalid language
    response = client.post(
        reverse('code-submission'),
        data=json.dumps({
            'code': 'print("hello")',
            'language': 'invalid'
        }),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 400
    assert 'language' in response.json()

def test_submission_flow(client, auth_headers):
    """Test the complete submission flow."""
    # Submit code
    response = client.post(
        reverse('code-submission'),
        data=json.dumps({
            'code': 'def solution(x): return x * 2',
            'language': 'python',
            'test_cases': [
                {
                    'input': '2',
                    'expected': '4'
                }
            ]
        }),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 202
    data = response.json()
    assert 'submission_id' in data
    assert 'status' in data
    assert data['status'] == 'pending'

    # Check status
    submission_id = data['submission_id']
    response = client.get(
        f"{reverse('submission-status')}?submission_id={submission_id}",
        **auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data

def test_invalid_submission_id(client, auth_headers):
    """Test status check with invalid submission ID."""
    response = client.get(
        f"{reverse('submission-status')}?submission_id={uuid.uuid4()}",
        **auth_headers
    )
    assert response.status_code == 404
    assert 'error' in response.json()

def test_missing_submission_id(client, auth_headers):
    """Test status check without submission ID."""
    response = client.get(reverse('submission-status'), **auth_headers)
    assert response.status_code == 400
    assert 'error' in response.json() 