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
        assert data['active_nodes'] >= 0

    def test_health_new_fields_optional(self, client):
        """New 'details' object must not break old parsers"""
        response = client.get('/health')
        data = response.get_json()
        assert 'details' in data
        assert isinstance(data['details'], dict)
        assert 'system_status' in data['details']
        assert 'services' in data['details']

    @patch('bridge_web.get_active_nodes')
    def test_health_survives_node_fetch_failure(self, mock_nodes, client):
        """Endpoint must not crash if node data unavailable"""
        mock_nodes.side_effect = Exception("Network error")
        response = client.get('/health')
        assert response.status_code == 200 # Must still return 200
        data = response.get_json()
        assert data['active_nodes'] == 0 # Graceful degradation

    @patch('os.path.exists')
    def test_health_survives_missing_tasks_file(self, mock_exists, client):
        """Endpoint must work even if tasks.json missing"""
        mock_exists.return_value = False
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['details']['open_tasks'] == 0

class TestRecentActivityEndpoint:
    """Test the newly added /recent-activity endpoint"""
    def test_recent_activity_returns_safe_response(self, client):
        """Endpoint must not crash even with no real data"""
        response = client.get('/recent-activity')
        assert response.status_code == 200
        data = response.get_json()
        assert 'activities' in data
        assert isinstance(data['activities'], list)
        assert 'status' in data

    def test_recent_activity_handles_errors_gracefully(self, client):
        """Errors must return 503 with safe fallback data"""
        # Testing both paths
        for path in ['/recent-activity', '/api/v1/recent-activity']:
            with patch('bridge_web.get_active_nodes', side_effect=Exception("DB error")):
                response = client.get(path)
                assert response.status_code in [200, 503]
                data = response.get_json()
                assert 'activities' in data # Must have field even if empty
