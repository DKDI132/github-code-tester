from fastapi import FastAPI
from app.operator import rout
from app.system_logowania import router
from app.baza import create_pool,close_pool


apka = FastAPI()

apka.include_router(router)
apka.include_router(rout)
@apka.on_event("startup")
async def zacznij():
    await create_pool()
@apka.on_event("shutdown")
async def koncz():
    await close_pool()
