from app.models import Register,Login
from app.security import hash_haslo,sprawdz_haslo
import asyncmy
pool = None

async def udane_logowanie(dane:Login):
    pytanie="SELECT id,haslo from users where email = %s"
    try:
        wynik= await fetchall(pytanie,(dane.mail,))
    except:
        return (0,None)
    wynik=wynik[0]
    if not sprawdz_haslo(dane.haslo,wynik[1]):
        return (-1,None)
    return (1,wynik[0])




async def czy_istnieje(a:str):
    pytanie="SELECT * from USERS where email = %s"
    wynik= await fetchall(pytanie,(a,))
    if wynik:
        return True
    return False

async def dodaj_uzytkownika(a:Register):
    kwerenda = "INSERT INTO users(email,haslo) Values (%s,%s)"
    email = a.mail
    haslo=a.haslo
    haslo_hashed =hash_haslo(haslo)
    wynik = await execute(kwerenda,(email,haslo_hashed))
    if wynik:
        return 1
    return 0

async def create_pool():
    global pool
    pool = await asyncmy.create_pool(
        host = "localhost",
        port= 3306,
        user = "root",
        password="root",
        db="testy",
        autocommit=True,
        minsize=2,
        maxsize=10
    )
async def close_pool():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()

async def fetchall(kwerenda:str,arg:tuple):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(kwerenda,arg)
            rows = await cursor.fetchall()
            return rows

async def execute(kwerenda:str,arg:tuple):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(kwerenda,arg)
            except:
                return False
            return True