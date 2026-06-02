import json
from pathlib import Path

import requests
from config import adres

TOKEN_PATH = Path(__file__).parent / "token.json"

def szczegoly(token,id):
    response = requests.get(
        f"{adres}/api-operacje/szczegoly?id={id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=10

    )
    dane = response.json()
    return dane["details"]


def lista_testowa(token):
    response = requests.get(
        f"{adres}/api-operacje/wyciagnij",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=10
    )
    dane = response.json()
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
        },
        timeout=10
    )
    dane = response.json()

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
        },
        timeout=10
    )
    dane = response.json()
    if response.status_code != 200:
        return dane["detail"]["details"]
    token = dane["token"]
    with open(TOKEN_PATH,'w', encoding="utf-8") as file:
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
        },
        timeout=10
    )
    dane = response.json()
    if response.status_code != 201:
        return dane["detail"]["details"]
    return dane["details"]

