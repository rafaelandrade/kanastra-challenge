class InvoiceException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidCSVFormatError(InvoiceException):
    pass


class BulkOperationError(InvoiceException):
    pass


class EmailSendingError(InvoiceException):
    pass


class InvoiceSendingError(InvoiceException):
    pass
