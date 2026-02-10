import pytest
import json
from unittest.mock import patch, MagicMock

class TestHealthBackwardCompatibility:
    """
    [ADMIN REQUIREMENT] Ensure /health endpoint maintains backward compatibility 
    with existing monitoring systems while adding new fields.
    """
    REQUIRED_OLD_FIELDS = ['status', 'version', 'ai', 'claude', 'proxy', 'admin', 'active_nodes']

    def test_health_preserves_all_old_fields(self, client):
        """Verify no breaking changes in existing field names"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        for field in self.REQUIRED_OLD_FIELDS:
            assert field in data, f"BREAKING CHANGE: Missing old field '{field}'"

    def test_health_field_types_unchanged(self, client):
        """Ensure field types match legacy contracts"""
        response = client.get('/health')
        data = response.get_json()
        
        # Type assertions
        assert isinstance(data['status'], str)
        assert isinstance(data['version'], str)
        assert isinstance(data['ai'], bool)
        assert isinstance(data['claude'], bool)
        assert isinstance(data['proxy'], bool)
        assert isinstance(data['admin'], bool)
        assert isinstance(data['active_nodes'], int)

    def test_health_new_fields_optional(self, client):
        """New 'details' object must not break old parsers"""
        response = client.get('/health')
        data = response.get_json()
        assert 'details' in data
        assert isinstance(data['details'], dict)
        assert 'system_status' in data['details']

    @patch('bridge_web.get_active_nodes')
    def test_health_survives_node_fetch_failure(self, mock_nodes, client):
        """Endpoint must not crash if node data unavailable"""
        mock_nodes.side_effect = Exception("Network error")
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['active_nodes'] == 0

class TestRecentActivityEndpoint:
    """Test the newly added /recent-activity endpoint"""
    def test_recent_activity_returns_safe_response(self, client):
        """Endpoint must not crash even with no real data"""
        response = client.get('/recent-activity')
        assert response.status_code == 200
        data = response.get_json()
        assert 'activities' in data
        assert isinstance(data['activities'], list)

@pytest.fixture
def client():
    """Flask test client fixture"""
    from bridge_web import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
