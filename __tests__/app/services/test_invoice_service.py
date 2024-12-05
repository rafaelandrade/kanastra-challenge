import unittest
from unittest.mock import patch, MagicMock, call
from app.services.invoice_service import Invoice


class TestInvoice(unittest.TestCase):
    @patch('app.services.invoice_service.mongo_client')
    @patch('app.services.invoice_service.mongo_db')
    @patch('app.services.invoice_service.Email')
    @patch('app.services.invoice_service.logger')
    def test_create_invoice(self, mock_logger, mock_email_class, mock_mongo_db, mock_mongo_client):
        mock_collection = MagicMock()
        mock_mongo_db.__getitem__.return_value = mock_collection

        mock_email_handler = MagicMock()
        mock_email_class.return_value = mock_email_handler

        csv_content = (
            "debtId,name,email,governmentId,debtAmount,debtDueDate\n"
            "1,John Doe,john@example.com,123456789,100.50,2024-01-19\n"
            "2,Jane Doe,jane@example.com,987654321,200.75,2024-02-20\n"
            "4,Batman,batman@example.com,987654321,200.75,2024-02-20\n"
        ).encode()

        invoice_service = Invoice(file_content=csv_content)

        bulk_write_result = MagicMock(upserted_count=2)
        mock_collection.bulk_write.return_value = bulk_write_result

        invoice_service.create_invoice()

        mock_logger.send_log.assert_any_call('[Invoice] - Generating Invoice...')
        mock_logger.send_log.assert_any_call('[Invoice] - Invoice generation complete.')

        self.assertEqual(mock_collection.bulk_write.call_count, 1)
        self.assertTrue(mock_collection.bulk_write.called)

        expected_calls = [
            call(email="john@example.com", debt_id="1", debt_amount=100.50),
            call(email="jane@example.com", debt_id="2", debt_amount=200.75)
        ]
        mock_email_handler.send_email.assert_has_calls(expected_calls, any_order=True)

    @patch('app.services.invoice_service.mongo_db')
    @patch('app.services.invoice_service.logger')
    def test_skip_processed_rows(self, mock_logger, mock_mongo_db):
        csv_content = (
            "debtId,name,email,governmentId,debtAmount,debtDueDate\n"
            "1,John Doe,john@example.com,123456789,100.50,2024-01-19\n"
            "2,Jane Doe,jane@example.com,987654321,200.75,2024-02-20\n"
        ).encode()

        progress_collection = MagicMock()
        mock_mongo_db.__getitem__.return_value = progress_collection
        progress_collection.find_one.return_value = {"checksum": "checksum_value", "processed_rows": ["1", "2"]}

        invoice_service = Invoice(file_content=csv_content)
        invoice_service.create_invoice()

        mock_logger.send_log.assert_any_call('[Invoice] - Skipping already processed debtId: 1')

    @patch('app.services.invoice_service.mongo_db')
    @patch('app.services.invoice_service.logger')
    def test_large_file_batch_processing(self, mock_logger, mock_mongo_db):
        csv_content = "\n".join(
            [f"{i},Name{i},email{i}@example.com,ID{i},{100 + i},2024-01-30" for i in range(1, 10002)]
        ).encode()
        csv_content = b"debtId,name,email,governmentId,debtAmount,debtDueDate\n" + csv_content

        collection = MagicMock()
        mock_mongo_db.__getitem__.return_value = collection

        bulk_write_result = MagicMock(upserted_count=10000)
        collection.bulk_write.return_value = bulk_write_result

        invoice_service = Invoice(file_content=csv_content)
        invoice_service.create_invoice()

        # Assert that batch processing occurred
        self.assertEqual(collection.bulk_write.call_count, 2)

    @patch('app.services.invoice_service.mongo_db')
    @patch('app.services.invoice_service.logger')
    def test_bulk_write_error_handling(self, mock_logger, mock_mongo_db):
        csv_content = (
            "debtId,name,email,governmentId,debtAmount,debtDueDate\n"
            "1,John Doe,john@example.com,123456789,100.50,2024-01-19\n"
        ).encode()

        collection = MagicMock()
        collection.bulk_write.side_effect = Exception("Bulk write error")
        mock_mongo_db.__getitem__.return_value = collection

        invoice_service = Invoice(file_content=csv_content)

        with self.assertRaises(Exception):
            invoice_service.create_invoice()

        mock_logger.send_log.assert_any_call("[Invoice] - Error during bulk operation: Bulk write error")

    @patch('app.services.invoice_service.Email')
    @patch('app.services.invoice_service.mongo_client')
    @patch('app.services.invoice_service.mongo_db')
    @patch('app.services.invoice_service.logger')
    def test_email_sending_error(self, mock_logger, mock_mongo_db, mock_mongo_client, mock_email_class):
        mock_collection = MagicMock()
        mock_mongo_db.__getitem__.return_value = mock_collection

        mock_email_handler = MagicMock()
        mock_email_class.return_value = mock_email_handler

        csv_content = (
            "debtId,name,email,governmentId,debtAmount,debtDueDate\n"
            "1,John Doe,john@example.com,123456789,100.50,2024-01-19\n"
        ).encode()

        bulk_write_result = MagicMock(upserted_count=1)
        mock_collection.bulk_write.return_value = bulk_write_result

        invoice_service = Invoice(file_content=csv_content)

        mock_email_handler.send_email.side_effect = Exception("SMTP error")

        with self.assertRaises(Exception):
            invoice_service.create_invoice()

        mock_logger.send_log.assert_any_call("[Invoice] - Failed to send email to john@example.com: SMTP error")

    def test_create_invoice_invalid_csv(self):
        invalid_csv_content = b""

        invoice_service = Invoice(file_content=invalid_csv_content)

        with self.assertRaises(Exception):
            invoice_service.create_invoice()
