from ninja import NinjaAPI, Schema
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

api = NinjaAPI(
    title="Avda Software - API Clínica",
    version="1.0.0",
    description="Backend para Gestão Clínica Integrada"
)

# --- SCHEMAS (Modelos de dados que a API recebe/envia) ---

class LoginSchema(Schema):
    email: str
    password: str

class UserOutSchema(Schema):
    id: int
    email: str
    nome_completo: str
    role: str

# --- ROTAS ---

@api.get("/status")
def check_status(request):
    return {"status": "operacional", "msg": "Servidores da Avda Software online em Eunápolis"}

@api.post("/auth/login", response=UserOutSchema)
def login_usuario(request, data: LoginSchema):
    # O authenticate do Django já sabe usar o e-mail por causa do USERNAME_FIELD
    user = authenticate(request, email=data.email, password=data.password)
    
    if user is not None:
        return user # O Ninja converte o objeto User para o formato do UserOutSchema automaticamente
    else:
        raise HttpError(401, "E-mail ou senha inválidos")