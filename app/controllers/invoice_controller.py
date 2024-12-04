from app.services.invoice_service import Invoice


class InvoiceController:

    @staticmethod
    async def invoice_generate(file):
        invoice = Invoice(file_content=file)
        invoice.create_invoice()
