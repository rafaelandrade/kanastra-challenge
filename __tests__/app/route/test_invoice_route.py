import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO


class TestInvoiceGenerate(unittest.TestCase):

    @patch("app.services.invoice_service.mongo_client")
    @patch("app.services.invoice_service.mongo_db")
    def test_invoice_generate(self, mock_mongo_db, mock_mongo_client):
        mock_collection = MagicMock()
        mock_progress_collection = MagicMock()

        mock_progress_collection.find_one.return_value = None

        mock_progress_collection.update_one.return_value = MagicMock()

        mock_mongo_db.__getitem__.side_effect = lambda name: {
            "invoices": mock_collection,
            "invoice_progress": mock_progress_collection
        }[name]

        mock_collection.bulk_write.return_value = MagicMock(upserted_count=0)

        client = TestClient(app)

        fake_csv_content = (
            "debtId,name,email,governmentId,debtAmount,debtDueDate\n"
            "1,John Doe,john@example.com,1234,100.5,2024-12-31\n"
        )
        files = {"file": ("test.csv", fake_csv_content, "text/csv")}

        response = client.post("/invoice/generate", files=files)

        self.assertEqual(response.status_code, 200)

        mock_collection.bulk_write.assert_called()
        mock_progress_collection.update_one.assert_called()

    def test_invoice_generate_invalid_file_extension(self):
        client = TestClient(app)
        file = BytesIO(b"dummy content")
        response = client.post(
            "/invoice/generate",
            files={"file": ("test.txt", file, "text/plain")},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "File must be a CSV"}