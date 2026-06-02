from fastapi import APIRouter
from fastapi.params import Header,Query
from requests.utils import default_headers
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.models import Testowe
from app.security import sprawdz_token
from app.baza import dodaj_do_sprawdzenia,wyjmij_testy,wyjmij_szczegoly
rout = APIRouter(prefix="/api-operacje")



@rout.post("/sprawdz")
async def sprawdzanie(request:Request,dane:Testowe,authorization:str= Header()):
    id_klienta=sprawdz_token(authorization.split()[1])
    status = await dodaj_do_sprawdzenia(id_klienta,dane.link)
    if status == 0:
        raise HTTPException(500, {"status": "blad","details": "Nie udalo sie utworzyc testu prosze sprobowac pozniej"})
    return JSONResponse(status_code=200,content={"status":"ok","details":"Test zostal poprawnie dodany i niedlugo zostanie wykonany"})

@rout.get("/wyciagnij")
async def wyciagnij(request:Request,Authorization:str=Header()):
    id_klienta = sprawdz_token(Authorization.split()[1])
    dane = await wyjmij_testy(id_klienta)
    return JSONResponse(status_code=200,content={"status":"ok","details":list(dane)})

@rout.get("/szczegoly")
async def szczegoly(request:Request,id:int=Query(),Authorization:str=Header()):
    id_klienta = sprawdz_token(Authorization.split()[1])
    dane = await wyjmij_szczegoly(id,id_klienta)
    return JSONResponse(status_code=200,content={"status":"ok","details":list(dane)})
