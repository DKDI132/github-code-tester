from pydantic import BaseModel, EmailStr, model_validator


class Register(BaseModel):
    mail:EmailStr
    haslo:str
    powtorzone:str
    @model_validator(mode="after")
    def sprawdz(self):
        if self.haslo != self.powtorzone:
            raise ValueError("zle dane")
        return self


class Login(BaseModel):
    mail:EmailStr
    haslo:str

class Testowe(BaseModel):
    link:str