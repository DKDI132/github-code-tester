import asyncio
import os
import subprocess
import stat
import shutil

from app.baza import create_pool,znajdz_nastepny_do_testu,dodaj_krok,zmien_status,zmien_wynik

def force_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

async def przeprowadz_testy(dane:tuple):
    folder = f"C:/tmp/repo-tests/job_{dane[0]}"
    try:
        wyniki = []

        await zmien_status(dane[0],"w_trakcie")

        wynik = subprocess.run(
            ["git", "clone", dane[2], folder],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
        )
        if wynik.returncode == 0:
            status = "success"
            wyniki.append(1)
        else:
            status = "fail"
            wyniki.append(0)
        status =await dodaj_krok(dane[0],0,"pobranie projektu","git clone",status,wynik.returncode,wynik.stdout,wynik.stderr)
        if 0 in wyniki:
            await zmien_status(dane[0], "gotowe")
            await zmien_wynik(dane[0], "fail")
            return 1
        #-----------------------------

        command = [
            "docker", "run", "--rm",
            "--memory", "512m",
            "--cpus", "1",
            "--pids-limit", "128",
            "--security-opt", "no-new-privileges",
            "-v", f"{folder}:/repo",
            "-w", "/repo",
            "python:3.12-slim",
            "sh", "-c", "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && python -m compileall ."
        ]

        result = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=300
        )
        if result.returncode == 0:
            status = "success"
            wyniki.append(1)
        else:
            status="fail"
            wyniki.append(0)
        status = await dodaj_krok(dane[0],1,"pobranie zaleznosci i kompilacja","sh -c if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && python -m compileall .",status,result.returncode,result.stdout,result.stderr)
        if 0 in wyniki:
            status = "fail"
        else:
            status = "success"
        await zmien_status(dane[0],"gotowe")
        await zmien_wynik(dane[0],status)
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = e.stderr or "Timeout podczas wykonywania komendy"
        await dodaj_krok(dane[0],2,"blad workera","timeout","fail",None,stdout,stderr)
        await zmien_status(dane[0],"gotowe")
        await zmien_wynik(dane[0],"fail")
    except Exception as e:
        await dodaj_krok(dane[0],2,"blad workera","worker exception","fail",None,"",str(e))
        await zmien_status(dane[0],"gotowe")
        await zmien_wynik(dane[0],"fail")
    finally:
        if os.path.exists(folder):
            shutil.rmtree(folder,onerror=force_remove_readonly)





async def main():
    await create_pool()

    while True:
        job = await znajdz_nastepny_do_testu()
        if job:
            await przeprowadz_testy(job)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
