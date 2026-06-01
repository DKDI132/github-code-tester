from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RangeNotSatisfiable
from starlette.status import HTTP_102_PROCESSING
from app.security import stworz_token
from app.models import Register, Login
from fastapi import APIRouter,Request
from app.baza import czy_istnieje,dodaj_uzytkownika,udane_logowanie
router = APIRouter(prefix="/api-log")



@router.post("/register")
async def rejestruj(request:Request,dane:Register):
    print(type(dane))
    if await czy_istnieje(dane.mail):
        raise HTTPException(409,{"status":"blad","details":"takie konto już istnieje"})
    if await dodaj_uzytkownika(dane):
        return JSONResponse(status_code=201,content={"status":"ok","details":"Rejestracja przebiegla pomyslnie"})
    raise HTTPException(500,{"status":"blad","details":"Rejestracja sie nie powiodla z naszej winy, prosze wrocic pozniej"})

@router.post("/login")
async def login(request:Request,dane:Login):
    if not await czy_istnieje(dane.mail):
        raise HTTPException(401,{"status":"blad","details":"nie ma takiego konta"})
    logowanie = await udane_logowanie(dane)
    if logowanie[0] == -1:
        raise HTTPException(401,{"status":"blad","details":"Haslo jest nieprawidlowe"})
    if logowanie[0] == 0:
        raise HTTPException(500, {"status": "blad","details": "Rejestracja sie nie powiodla z naszej winy, prosze wrocic pozniej"})
    id = logowanie[1]
    token_jwt = stworz_token(id)
    return JSONResponse(status_code=200,content={"status":"ok","details":"logowanie przebieglo pomyslnie","token":token_jwt})

