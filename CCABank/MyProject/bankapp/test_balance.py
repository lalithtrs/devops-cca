from django.test import TestCase
from unittest.mock import patch

class BankBalanceTests(TestCase):

    @patch('bankapp.db_repository.getuser')
    @patch('bankapp.db_repository.validatecsrftoken')
    @patch('bankapp.db_repository.getuserbalance')
    def test_check_balance_success(self, mock_get_balance, mock_validate_csrf, mock_get_user):
        """Test that the user's bank balance is successfully retrieved and rendered when a valid CSRF token is provided."""
        # 1. Mock the user session to represent a logged-in user
        mock_get_user.return_value = {
            "login_name": "alice",
            "role_name": "ROLE_CUSTOMER",
            "token": "valid-csrf-token-123"
        }
        
        # 2. Mock CSRF validation to succeed
        mock_validate_csrf.return_value = True
        
        # 3. Mock the database query returning the balance amount
        mock_get_balance.return_value = {"balance_amount": 5432.10}
        
        # 4. Set the active session cookie
        self.client.cookies['SESSION_ID'] = "active-session-uuid"
        
        # 5. Perform the POST request to the home page with the token
        response = self.client.post('/bank/', {
            'token_csrf': 'valid-csrf-token-123'
        })
        
        # 6. Verify assertions
        self.assertEqual(response.status_code, 200)
        
        # Verify db_repository calls
        mock_validate_csrf.assert_called_once_with('valid-csrf-token-123', 'active-session-uuid')
        mock_get_balance.assert_called_once_with('active-session-uuid')
        
        # Assert that the correct balance is in the response context and rendered template
        self.assertEqual(response.context['balance_amount'], 5432.10)
        self.assertContains(response, "5432.1")

    @patch('bankapp.db_repository.getuser')
    @patch('bankapp.db_repository.validatecsrftoken')
    @patch('bankapp.db_repository.getuserbalance')
    def test_check_balance_csrf_failure(self, mock_get_balance, mock_validate_csrf, mock_get_user):
        """Test that the bank balance is not retrieved if CSRF token validation fails."""
        # 1. Mock user session
        mock_get_user.return_value = {
            "login_name": "alice",
            "role_name": "ROLE_CUSTOMER",
            "token": "valid-csrf-token-123"
        }
        
        # 2. Mock CSRF validation to fail
        mock_validate_csrf.return_value = False
        
        # 3. Set the active session cookie
        self.client.cookies['SESSION_ID'] = "active-session-uuid"
        
        # 4. Perform the POST request with an invalid/malicious token
        response = self.client.post('/bank/', {
            'token_csrf': 'attacker-csrf-token'
        })
        
        # 5. Verify assertions
        self.assertEqual(response.status_code, 200)
        
        # Verify db_repository validatecsrftoken was called, but getuserbalance was NEVER called
        mock_validate_csrf.assert_called_once_with('attacker-csrf-token', 'active-session-uuid')
        mock_get_balance.assert_not_called()
        
        # Assert that balance_amount in context is None and not rendered in the template
        self.assertIsNone(response.context['balance_amount'])
        self.assertNotContains(response, "balance_amount")
