import uvicorn
from fastapi import FastAPI
from app.routers import invoice_route

app = FastAPI()

app.include_router(invoice_route.router, prefix='/invoice')


@app.get("/")
def read_root():
    return {"message": "Hello World!"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
