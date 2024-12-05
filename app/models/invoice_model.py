import datetime
from pydantic import BaseModel


class InvoiceModel(BaseModel):
    id: str
    full_name: str
    gov_id: int
    email: str
    debt_amount: float
    debt_due_date: datetime.date
