from fastapi import FastAPI
from app.routers import invoice_route

app = FastAPI()

app.include_router(invoice_route.router, prefix='/invoice')


@app.get("/")
def read_root():
    return {"message": "Hello World!"}
