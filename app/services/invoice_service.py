from datetime import datetime

import pandas as pd
from io import BytesIO
from app.helpers.logger import logger
from app.services.email_service import Email

from pymongo import UpdateOne
from app.database.mongo import mongo_client, mongo_db
from app.helpers.checksum_helper import calculate_checksum
from app.errors.invoice_error import BulkOperationError, InvoiceSendingError, EmailSendingError


class Invoice:
    def __init__(self, file_content: bytes):
        self.file_content = file_content
        self.email_handler = Email()
        self.client = mongo_client
        self.db = mongo_db
        self.collection = self.db['invoices']
        self.progress_collection = self.db['invoice_progress']
        self.csv_checksum = calculate_checksum(file_content=file_content)

    def create_invoice(self):
        logger.send_log('[Invoice] - Generating Invoice...')
        try:
            df = pd.read_csv(BytesIO(self.file_content))

            logger.send_log(f'[Invoice] - Read {len(df)} rows from file.')

            processed_rows = self.load_progress()
            operations = []
            emails_to_send = []
            invoices_to_send = []

            for index, row in df.iterrows():
                logger.send_log(f'[Invoice] Handling invoice {row.to_dict()}')

                if str(row["debtId"]) in processed_rows:
                    logger.send_log(f'[Invoice] - Skipping already processed debtId: {row["debtId"]}')
                    continue

                operations.append(UpdateOne(
                    {"debt_id": str(row["debtId"])},
                    {
                        "$setOnInsert": {
                            "full_name": row["name"],
                            "email": row["email"],
                            "gov_id": row["governmentId"],
                            "debt_amount": float(row["debtAmount"]),
                            "debt_due_date": datetime.strptime(row["debtDueDate"], "%Y-%m-%d"),
                        }
                    },
                    upsert=True
                ))

                emails_to_send.append({
                    "email": row["email"],
                    "debt_id": str(row["debtId"]),
                    "debt_amount": float(row["debtAmount"])
                })

                invoices_to_send.append({
                    "email": row["email"],
                    "debt_id": str(row["debtId"]),
                    "debt_amount": float(row["debtAmount"]),
                    "debt_due_date": datetime.strptime(row["debtDueDate"], "%Y-%m-%d"),
                    "full_name": row["name"],
                })

                processed_rows.add(row["debtId"])

                if len(operations) == 10000:
                    self._execute_operations_and_send_email(operations=operations,
                                                            emails_to_send=emails_to_send,
                                                            invoices_to_send=invoices_to_send)
                    self.save_progress(processed_rows=processed_rows)
                    operations = []
                    emails_to_send = []

            if operations:
                self._execute_operations_and_send_email(operations=operations,
                                                        emails_to_send=emails_to_send,
                                                        invoices_to_send=invoices_to_send)
                self.save_progress(processed_rows=processed_rows)

            logger.send_log('[Invoice] - Invoice generation complete.')

        except Exception as exception:
            logger.send_log(f"[Invoice] - Critical error processing file: {str(exception)}")

            raise BulkOperationError(f"Critical error during bulk operation: {str(exception)}")

    def _execute_operations_and_send_email(self, operations, emails_to_send, invoices_to_send):
        try:
            result = self.collection.bulk_write(operations)
            logger.send_log(f"[Invoice] - Bulk operation complete: {result.bulk_api_result}")

            inserted_count = result.upserted_count
            if inserted_count > 0:
                for email_info in emails_to_send[:inserted_count]:
                    self._send_email(email=email_info["email"],
                                     debt_id=email_info["debt_id"],
                                     debt_amount=email_info["debt_amount"])

                for invoice_info in invoices_to_send[:inserted_count]:
                    self.send_invoice(email=invoice_info["email"],
                                      debt_id=invoice_info["debt_id"],
                                      debt_amount=invoice_info["debt_amount"],
                                      full_name=invoice_info["full_name"],
                                      debt_due_date=invoice_info["debt_due_date"])

        except Exception as exception:
            logger.send_log(f"[Invoice] - Error during bulk operation: {str(exception)}")
            raise BulkOperationError(f"Critical error during bulk operation: {str(exception)}")

    @staticmethod
    def send_invoice(email: str, debt_id: str, full_name: str, debt_amount: float, debt_due_date):
        try:
            logger.info(f'[Invoice] Sending Invoice with follow parameters: '
                        f'Email {email}, DebtId {debt_id}, Full Name {full_name}, Debt Amount {debt_amount} and '
                        f'Debt Due Date {debt_due_date}')
        except Exception as exception:
            logger.send_log(f"[Invoice] - Error during send invoice: {str(exception)}")
            raise InvoiceSendingError(f"Error during send of invoice: {str(exception)}")

    def _send_email(self, email: str, debt_id: str, debt_amount: int):
        try:
            self.email_handler.send_email(email=email, debt_id=debt_id, debt_amount=debt_amount)
            logger.send_log(f"[Invoice] - Email sent to {email} for debt ID {debt_id}")
        except Exception as exception:
            logger.send_log(f"[Invoice] - Failed to send email to {email}: {str(exception)}")
            raise EmailSendingError(f"Failed to send email {email}: {str(exception)}")

    def load_progress(self):
        record = self.progress_collection.find_one({"checksum": self.csv_checksum})
        if record:
            return set(record.get("processed_rows", []))
        return set()

    def save_progress(self, processed_rows):
        self.progress_collection.update_one(
            {"checksum": self.csv_checksum},
            {"$set": {"processed_rows": list(processed_rows)}},
            upsert=True
        )