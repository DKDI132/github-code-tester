from fastapi import FastAPI
from app.system_logowania import router
from app.baza import create_pool,close_pool
from dotenv import load_dotenv


apka = FastAPI()

apka.include_router(router)

@apka.on_event("startup")
async def zacznij():
    await create_pool()
    load_dotenv(".env")
@apka.on_event("shutdown")
async def koncz():
    await close_pool()
