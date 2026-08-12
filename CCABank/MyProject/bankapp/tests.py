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

    @patch('bankapp.db_repository.getuser')
    @patch('bankapp.db_repository.getuserbalance')
    @patch('bankapp.db_repository.validatecsrftoken')
    def check_balance(self, mock_validatecsrftoken, mock_getuserbalance, mock_getuser):
        mock_getuser.return_value = {"login_name": "Gokul", "role_name": "ROLE_PUBLIC", "token": "valid-csrf-token-123"}
        mock_validatecsrftoken.return_value = True
        mock_getuserbalance.return_value = {"balance_amount": 5000}
        self.client.cookies["SESSION_ID"] = "active-session-uuid"
        response = self.client.post("/bank/", {"token_csrf": "valid-csrf-token-123"})
        self.assertEqual(response.status_code, 200)
        mock_validatecsrftoken.assert_called_once_with("valid-csrf-token-123", "active-session-uuid")
        mock_getuserbalance.assert_called_once_with("active-session-uuid")
        self.assertEqual(response.context["balance_amount"], 5000)
        self.assertContains(response, "5000")

