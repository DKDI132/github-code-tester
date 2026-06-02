import sys
import json
from requesty import dodaj_do_kolejki,loguj,rejestruj,lista_testowa
from getpass import getpass

def wyjmij_token():
    try:
        with open("token.json",'r') as file:
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

    for numer, test in enumerate(lista_testow, start=1):
        test_id = test[0]
        link = test[1]
        status = test[2]
        wynik = test[3] if test[3] is not None else "-"

        print(f"{numer}. [{status}/{wynik}] ID {test_id}")
        print(f"   {link}")

    quit()