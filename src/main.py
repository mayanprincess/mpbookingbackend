from fastapi import FastAPI
from src.routes.reservation import router as reservation_router
from src.routes.payment import router as payment_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reservation_router)
app.include_router(payment_router)