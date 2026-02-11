#Este documento define los esquemas de datos relacionados con la autenticación, como el token de acceso y la solicitud de inicio de sesión. Estos esquemas se utilizan para 
#validar y estructurar los datos que se envían y reciben durante el proceso de autenticación.
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str
