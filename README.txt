# Trokaí Backend

**Pré-requisitos**
- Python 3.x instalado

**1. Criar e ativar ambiente virtual**

Windows:
python -m venv .venv
.venv\Scripts\activate


Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate


**2. Instalar dependências**
pip install -r requirements.txt


**3. Configurar variáveis de ambiente (opcional)**
Crie um arquivo `.env` na raiz:

DEBUG=True
SECRET_KEY=<sua_chave>
DATABASE_URL=sqlite:///db.sqlite3


**4. Executar migrações**
python manage.py migrate


**5. Criar superusuário (opcional)**
python manage.py createsuperuser


**6. Iniciar o servidor**
python manage.py runserver


**7. Acessar a API e Swagger**
- API: http://localhost:8000/api/
- Documentação Swagger: http://localhost:8000/swagger/

