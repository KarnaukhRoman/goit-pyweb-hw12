from fastapi import FastAPI

from src.routes.route_contacts import router as router_contacts
from src.routes.route_users import router as router_users

app = FastAPI()

app.include_router(router_users, prefix="/api", tags=["auth"])
app.include_router(router_contacts, prefix="/api", tags=["contacts"])
