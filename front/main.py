import sys
import json
from pathlib import Path

from requesty import dodaj_do_kolejki,loguj,rejestruj,lista_testowa,szczegoly
from getpass import getpass

TOKEN_PATH = Path(__file__).parent / "token.json"

def wypisz_szczegoly(informacje):
    if not informacje:
        print("Test jeszcze nie ma krokow albo nie istnieje.")
        return

    pierwszy = informacje[0]

    test_id = pierwszy[9]
    repo_url = pierwszy[11]
    test_status = pierwszy[12]
    test_result = pierwszy[13] if pierwszy[13] is not None else "brak"

    print("\nSzczegoly testu")
    print("=" * 60)
    print(f"ID:     {test_id}")
    print(f"Repo:   {repo_url}")
    print(f"Status: {test_status}")
    print(f"Wynik:  {test_result}")
    print("=" * 60)

    for step in informacje:
        step_order = step[2]
        name = step[3]
        command = step[4]
        status = step[5]
        exit_code = step[6]
        stdout = step[7] or ""
        stderr = step[8] or ""

        print(f"\nKrok {step_order}: {name}")
        print("-" * 60)
        print(f"Status:    {status}")
        print(f"Exit code: {exit_code}")
        print(f"Komenda:   {command}")

        if stdout.strip():
            print("\nSTDOUT:")
            print(stdout[:1000])

        if stderr.strip():
            print("\nSTDERR:")
            print(stderr[:1000])

        print("-" * 60)

def wypisz_liste_testow(lista_testow):
    if not lista_testow:
        print("Nie masz jeszcze zadnych testow.")
        return

    print("\nTwoje ostatnie testy")
    print("=" * 60)

    for numer, test in enumerate(lista_testow, start=1):
        test_id = test[0]
        link = test[1]
        status = test[2]
        wynik = test[3] if test[3] is not None else "brak"

        print(f"{numer}. ID: {test_id}")
        print(f"   Repo:   {link}")
        print(f"   Status: {status}")
        print(f"   Wynik:  {wynik}")
        print("-" * 60)

def wyjmij_token():
    try:
        with open(TOKEN_PATH,'r', encoding="utf-8") as file:
            p=file.read()
            if not p:
                print("prosze najpierw sie zalogowac -l")
                quit()
            dane=json.loads(p)
            jwt = dane["token"]
            return jwt

    except Exception as e:
        print(e)
        print("prosze najpierw sie zalogowac -l")
        quit()

try:
    a=sys.argv[1]
except:
    print("podaj arg")
    quit()

if a == '-t':
    try:
        link = sys.argv[2]
    except:
        print("podaj link do repetytorium")
        quit()
    token=wyjmij_token()
    print(dodaj_do_kolejki(token,link))
    quit()
if a == "-l":
    mail=input("Podaj maila: ")
    haslo = getpass("Haslo: ")
    print(loguj(mail,haslo))
    quit()

if a == "-r":
    mail = input("Podaj maila: ")
    haslo = getpass("Haslo: ")
    powtorz_haslo=getpass("Powtorz haslo: ")
    print(rejestruj(mail,haslo,powtorz_haslo))
    quit()
if a == "-w":
    token = wyjmij_token()
    lista_testow = lista_testowa(token)

    if not lista_testow:
        print("Nie masz jeszcze zadnych testow")
        quit()

    print("Twoje ostatnie testy:\n")
    wypisz_liste_testow(lista_testow)
    try:
        odpowiedz=int(input("Szczegoly ktorego testu chcesz poznac: "))
        if odpowiedz < 1 or odpowiedz > len(lista_testow):
            print("Nie ma takiego numeru testu")
            quit()
    except ValueError:
        print("Podaj numer testu")
        quit()
    informacje = szczegoly(token,lista_testow[odpowiedz-1][0])
    wypisz_szczegoly(informacje)
    quit()
