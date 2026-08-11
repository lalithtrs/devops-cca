from django.test import TestCase
from unittest.mock import patch

class BankAppTests(TestCase):
    @patch('bankapp.db_repository.getuser')
    def test_homepage_anonymous(self, mock_getuser):
        """Test that the homepage renders successfully for an anonymous/unauthenticated user."""
        mock_getuser.return_value = {"login_name": "", "role_name": "ROLE_PUBLIC", "token": "mock-token-123"}
        
        response = self.client.get('/bank/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not logged in. Please log in or register first.")

    @patch('bankapp.db_repository.getuser')
    def test_aboutus_page(self, mock_getuser):
        """Test that the about-us page renders successfully."""
        mock_getuser.return_value = {"login_name": "", "role_name": "ROLE_PUBLIC", "token": "mock-token-123"}
        
        response = self.client.get('/bank/about-us')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Us")
