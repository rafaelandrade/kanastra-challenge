from fastapi import APIRouter, UploadFile, HTTPException
from app.controllers.invoice_controller import InvoiceController
from app.errors.invoice_error import InvalidCSVFormatError, InvoiceSendingError, BulkOperationError, EmailSendingError

router = APIRouter()


@router.post('/generate')
async def invoice_generate(file: UploadFile):
    invoice = InvoiceController()
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        await invoice.invoice_generate(file=contents)
        return { "result": "Invoice generation completed." }
    except InvalidCSVFormatError as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    except BulkOperationError as exception:
        raise HTTPException(status_code=500, detail=str(exception))
    except EmailSendingError as exception:
        raise HTTPException(status_code=502, detail=str(exception))
    except InvoiceSendingError as exception:
        raise HTTPException(status_code=502, detail=str(exception))
    except Exception as _:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
