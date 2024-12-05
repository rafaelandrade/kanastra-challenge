import unittest
from unittest.mock import patch
from app.services.email_service import Email, logger

class TestEmail(unittest.TestCase):

    @patch('app.services.email_service.logger')
    def test_email_send(self, mock_logger):
        email = Email()
        email.send_email(email="test@test.com", debt_id="1", debt_amount=223)

        mock_logger.send_log.assert_any_call(f'[Email] Sending '
                                             f'Email with follow parameters: email '
                                             f'test@test.com - DebtId 1 - DebtAmount 223')


