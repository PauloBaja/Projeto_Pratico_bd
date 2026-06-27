# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# URL apontando para a porta 5433 do seu docker-compose
DATABASE_URL = "postgresql://admin:supersecretpassword@localhost:5433/universidade_db"

# O engine é o motor de comunicação
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Testar a conexão antes de usá-la (evita queda de conexão)
    echo=False            # Mude para True se quiser ver os comandos SQL puros no terminal
)

# Fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sessão com escopo seguro para reutilização em threads
db_session = scoped_session(SessionLocal)

def get_db():
    """
    Função utilitária (Generator) para abrir e fechar as sessões de forma segura.
    Muito utilizada em injeção de dependências (como no FastAPI).
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()