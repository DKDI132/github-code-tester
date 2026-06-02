from app.models import Register,Login,Testowe
from app.security import hash_haslo,sprawdz_haslo
import asyncmy
pool = None
async def wyjmij_szczegoly(id:int,id_klienta:int):
    kwerenda = "SELECT * FROM repo_test_steps inner join repo_tests on repo_test_steps.repo_test_id = repo_tests.id where repo_tests.user_id = %s and repo_tests.id = %s ORDER BY repo_test_steps.step_order"
    wyniki = await fetchall(kwerenda,(id_klienta,id))
    return wyniki
async def wyjmij_testy(id:int):
    kwerenda = "SELECT id,repo_url,status,result from repo_tests where user_id = %s ORDER BY id DESC LIMIT 10"
    wyniki = await fetchall(kwerenda,(id,))
    return wyniki

async def zmien_wynik(id:int,wynik:str):
    kwerenda = "update repo_tests SET result = %s Where id = %s"
    status = await execute(kwerenda,(wynik,id))
    return status
async def zmien_status(id:int,status:str):
    kwerenda = "UPDATE repo_tests SET status = %s WHERE id = %s"
    status = await execute(kwerenda,(status,id))
    return status

async def dodaj_krok(id_testu,kolejnosc,name,command,status,exit_code,stdout,stderr):
    kwerenda = "INSERT INTO repo_test_steps(repo_test_id,step_order,name,command,status,exit_code,stdout,stderr) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    status = await execute(kwerenda,(id_testu,kolejnosc,name,command,status,exit_code,stdout,stderr))
    return status
async def znajdz_nastepny_do_testu():
    kwerenda = "SELECT * from repo_tests WHERE status = %s ORDER BY id LIMIT 1"
    wynik = await fetchall(kwerenda,("czeka",))
    if wynik:
        return wynik[0]
    return None

async def dodaj_do_sprawdzenia(id_klienta:int,link:str):
    kwerenda = "INSERT INTO repo_tests(user_id,repo_url) values (%s,%s)"
    status = await execute(kwerenda,(id_klienta,link))
    if status:
        return 1
    return 0

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