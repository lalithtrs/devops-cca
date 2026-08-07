import os
import sys
import unittest
import json

# Add src directory to system path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from app import app
from model_pipeline import predict_student_score, get_dataset_analytics

class MLAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Test that the /api/health endpoint returns a healthy status and includes model metrics."""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('model_type', data)
        self.assertIn('metrics', data)

    def test_presets_endpoint(self):
        """Test that /api/presets returns the predefined student profiles."""
        response = self.app.get('/api/presets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('presets', data)
        self.assertIn('high_achiever', data['presets'])

    def test_predict_endpoint_valid(self):
        """Test that the prediction API returns successfully with valid inputs."""
        payload = {
            "study_time_hours": 6.5,
            "attendance_percent": 95.0,
            "sleep_hours": 8.0,
            "gender": "Female",
            "parental_education": "Bachelors",
            "internet_access": "Yes",
            "extracurricular_activities": "Yes",
            "part_time_job": "No"
        }
        response = self.app.post('/api/predict', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('predicted_score', data['data'])
        self.assertIn('grade', data['data'])
        self.assertIn('status', data['data'])
        self.assertIn('badge_color', data['data'])
        self.assertIn('recommendations', data['data'])

    def test_predict_endpoint_empty_payload(self):
        """Test that the prediction API returns a 400 Bad Request when given an empty JSON body."""
        response = self.app.post('/api/predict', 
                                 data=json.dumps({}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_model_pipeline_direct(self):
        """Test the underlying model pipeline directly for output structure and value bounds."""
        sample_input = {
            "study_time_hours": 4.5,
            "attendance_percent": 88.0,
            "sleep_hours": 7.0
        }
        result = predict_student_score(sample_input)
        self.assertIn('predicted_score', result)
        self.assertTrue(0.0 <= result['predicted_score'] <= 100.0)
        self.assertIn('grade', result)
        self.assertIn('recommendations', result)

    def test_analytics_endpoint(self):
        """Test that the analytics API returns aggregated historical statistics."""
        response = self.app.get('/api/analytics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('total_students', data['data'])
        self.assertIn('avg_score', data['data'])
        self.assertIn('grade_distribution', data['data'])

if __name__ == '__main__':
    unittest.main()
