# Czat E2E

Prosty system do kolejkowania i sprawdzania publicznych repozytoriow GitHub. Uzytkownik loguje sie, wysyla link do repozytorium, a osobny worker pobiera kod, uruchamia go w Dockerze i zapisuje wynik testu w bazie.

## Co robi aplikacja

- rejestruje uzytkownikow,
- loguje uzytkownikow i zwraca JWT,
- przyjmuje link do repozytorium GitHub,
- zapisuje test do kolejki w MySQL,
- worker pobiera najstarszy oczekujacy test,
- klonuje repozytorium przez `git clone`,
- uruchamia test w kontenerze Docker z Pythonem,
- instaluje `requirements.txt`, jesli istnieje,
- sprawdza skladnie przez `python -m compileall .`,
- zapisuje kroki testu i wynik w bazie,
- CLI pozwala logowac sie, rejestrowac, dodawac repo i ogladac wyniki.

## Wymagania

- Python 3.12 lub nowszy,
- MySQL na `127.0.0.1:3306`,
- baza danych `testy`,
- Git,
- Docker Desktop,
- zainstalowane zaleznosci Pythona projektu.

Docker Desktop musi byc uruchomiony przed startem workera. Sama komenda `docker` jest tylko klientem, a worker potrzebuje dzialajacego Docker Engine.

## Konfiguracja

W katalogu projektu utworz plik `.env`:

```env
SECRET_KEY=twoj_sekretny_klucz
```

Aktualne polaczenie z baza jest ustawione w `app/baza.py`:

```text
host: 127.0.0.1 / localhost
port: 3306
user: root
password: root
db: testy
```

## Tabele w bazie

Aplikacja korzysta z tabel uzytkownikow oraz dwoch tabel do testow repozytoriow.

```sql
CREATE TABLE repo_tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    repo_url VARCHAR(500) NOT NULL,
    status ENUM('czeka','w_trakcie','gotowe') NOT NULL DEFAULT 'czeka',
    result ENUM('success','fail') NULL
);
```

```sql
CREATE TABLE repo_test_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repo_test_id INT NOT NULL,
    step_order INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    command TEXT NULL,
    status ENUM('czeka','w_trakcie','success','fail','skipped') NOT NULL DEFAULT 'czeka',
    exit_code INT NULL,
    stdout TEXT NULL,
    stderr TEXT NULL,
    FOREIGN KEY (repo_test_id) REFERENCES repo_tests(id) ON DELETE CASCADE
);
```

## Uruchomienie backendu

Z glownego katalogu projektu:

```powershell
uvicorn main:app --reload
```

Backend powinien byc dostepny pod:

```text
http://127.0.0.1:8000
```

Dokumentacja FastAPI:

```text
http://127.0.0.1:8000/docs
```

## Uruchomienie workera

Najpierw uruchom Docker Desktop i poczekaj, az Docker Engine wystartuje.

Mozesz sprawdzic:

```powershell
docker info
```

Potem w osobnym terminalu:

```powershell
python -m app.testowanie
```

Worker dziala jako osobny proces. Backend tylko dodaje testy do kolejki, a worker sam pobiera rekordy ze statusem `czeka`.

## Endpointy

### Rejestracja

```http
POST /api-log/register
```

Body:

```json
{
  "mail": "user@example.com",
  "haslo": "haslo",
  "powtorzone": "haslo"
}
```

### Logowanie

```http
POST /api-log/login
```

Body:

```json
{
  "mail": "user@example.com",
  "haslo": "haslo"
}
```

Odpowiedz zawiera token JWT:

```json
{
  "status": "ok",
  "details": "logowanie przebieglo pomyslnie",
  "token": "..."
}
```

### Dodanie repozytorium do kolejki

```http
POST /api-operacje/sprawdz
```

Header:

```http
Authorization: Bearer <JWT>
```

Body:

```json
{
  "link": "https://github.com/user/repo"
}
```

### Lista testow uzytkownika

```http
GET /api-operacje/wyciagnij
```

Header:

```http
Authorization: Bearer <JWT>
```

Zwraca ostatnie testy uzytkownika.

### Szczegoly testu

```http
GET /api-operacje/szczegoly?id=<ID_TESTU>
```

Header:

```http
Authorization: Bearer <JWT>
```

Zwraca kroki danego testu, jesli test nalezy do zalogowanego uzytkownika.

## CLI

Frontend CMD znajduje sie w katalogu `front`.

### Rejestracja

```powershell
python front/main.py -r
```

### Logowanie

```powershell
python front/main.py -l
```

Po zalogowaniu token jest zapisywany lokalnie w:

```text
front/token.json
```

Ten plik jest ignorowany przez Git.

### Dodanie repozytorium do testu

```powershell
python front/main.py -t https://github.com/user/repo
```

### Lista wynikow

```powershell
python front/main.py -w
```

CLI pobiera liste testow, pokazuje je jako numerowana liste, a potem pozwala wybrac test do wyswietlenia szczegolow.

## Jak dziala worker

Worker wykonuje uproszczony test Python-only:

1. pobiera najstarszy rekord z `repo_tests`, gdzie `status = 'czeka'`,
2. ustawia status glownego testu na `w_trakcie`,
3. klonuje repozytorium przez `git clone`,
4. zapisuje krok `pobranie projektu`,
5. odpala Docker:

```text
python:3.12-slim
```

6. w kontenerze wykonuje:

```sh
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && python -m compileall .
```

7. zapisuje wynik kroku,
8. ustawia `repo_tests.status = 'gotowe'`,
9. ustawia `repo_tests.result = 'success'` albo `fail`,
10. usuwa katalog tymczasowy.

## Przykladowy test

Mozesz sprawdzic prostym repozytorium lub gistem:

```powershell
python front/main.py -t https://gist.github.com/hbisneto/42349b9d709387e90c93dfeee4a105e1.git
```

Potem:

```powershell
python front/main.py -w
```

## Typowe problemy

### Docker nie dziala

Jesli widzisz:

```text
failed to connect to the docker API
```

uruchom Docker Desktop i sprawdz:

```powershell
docker info
```

### Blad usuwania folderu `.git`

Na Windowsie pliki z `.git` moga miec atrybut readonly albo byc chwilowo trzymane przez proces. Worker uzywa sprzatania z `chmod`, ale jesli problem wroci, sprawdz czy repo nie jest otwarte w innym programie.

### Token nie dziala

Token wysyla sie w headerze:

```http
Authorization: Bearer <JWT>
```

Jesli CLI nie znajduje tokena, zaloguj sie ponownie:

```powershell
python front/main.py -l
```
