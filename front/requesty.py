import json

import requests
from config import adres

def lista_testowa(token):
    response = requests.get(
        f"{adres}/api-operacje/wyciagnij",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    dane = json.loads(response.text)
    lista=dane["details"]
    lista=list(lista)
    return lista

def dodaj_do_kolejki(token,link):
    response = requests.post(
        f"{adres}/api-operacje/sprawdz",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "link": f"{link}"
        }
    )
    dane = json.loads(response.text)

    if response.status_code != 200:
        return dane["detail"]["details"]
    else:
        return dane["details"]


def loguj(mail,haslo):
    response = requests.post(
        f"{adres}/api-log/login",
        json={
            "mail": f"{mail}",
            "haslo":f"{haslo}"
        }
    )
    dane = json.loads(response.text)
    if response.status_code != 200:
        return dane["detail"]["details"]
    token = dane["token"]
    with open("token.json",'w') as file:
        json.dump({"token": token}, file)
    return dane["details"]

def rejestruj(mail,haslo,powtorz):
    if haslo != powtorz:
        return "Hasla musza byc takie same"
    response = requests.post(
        f"{adres}/api-log/register",
        json={
            "mail": f"{mail}",
            "haslo": f"{haslo}",
            "powtorzone":f"{powtorz}"
        }
    )
    dane = json.loads(response.text)
    if response.status_code != 201:
        return dane["detail"]["details"]
    return dane["details"]

