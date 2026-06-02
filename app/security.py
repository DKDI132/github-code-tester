import os
from jose import JWTError, jwt
from fastapi import HTTPException, status


import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")

def hash_haslo(haslo:str):
    return bcrypt.hashpw(haslo.encode("utf-8"),bcrypt.gensalt())

def sprawdz_haslo(haslo:str,haslo_hash:str):
    return bcrypt.checkpw(haslo.encode("utf-8"),haslo_hash.encode("utf-8"))

def stworz_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

def sprawdz_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status":"blad","details":"nieprawidlowy token"}
            )

        return int(user_id)


    except (JWTError, ValueError):

        raise HTTPException(

            status_code=401,

            detail={"status": "blad", "details": "nieprawidlowy token"}

        )