import pandas as pd
from io import BytesIO
from app.helpers.logger import logger


class Invoice:
    def __init__(self, file_content: bytes):
        self.file_content = file_content

    def create_invoice(self):
        logger.send_log('[Invoice] - Generating Invoice...')
        try:
            df = pd.read_csv(BytesIO(self.file_content))
            print(df)
        except Exception as exception:
            raise exception
