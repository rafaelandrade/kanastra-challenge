from fastapi import APIRouter, UploadFile, HTTPException
from app.controllers.invoice_controller import InvoiceController

router = APIRouter()


@router.post('/generate')
async def invoice_generate(file: UploadFile):
    print("hereeee -> ")
    invoice = InvoiceController()
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        await invoice.invoice_generate(file=contents)
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Error reading CSF file: {str(exception)}")
