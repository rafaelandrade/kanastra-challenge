from app.helpers.logger import logger


class Email:
    @staticmethod
    def send_email(email: str, debt_id: str, debt_amount: int):
        logger.send_log(f'[Email] Sending Email with follow parameters: email {email} - DebtId {debt_id} - DebtAmount {debt_amount}')
        return

