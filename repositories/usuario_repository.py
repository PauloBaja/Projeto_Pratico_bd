# repositories/usuario_repository.py
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Usuario

class UsuarioRepository:
    
    @staticmethod
    def create(db: Session, nome: str, cpf: Decimal, login: Optional[str] = None, senha: Optional[str] = None) -> Usuario:
        """CREATE: Instancia e salva um novo usuário no banco."""
        novo_usuario = Usuario(
            cpf=cpf,
            nome=nome,
            login=login,
            senha=senha
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario) 
        return novo_usuario

    @staticmethod
    def get_by_cpf(db: Session, cpf: Decimal) -> Optional[Usuario]:
        """READ: Busca um usuário específico pelo CPF."""
        return db.query(Usuario).filter(Usuario.cpf == cpf).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """READ: Retorna uma lista paginada de usuários."""
        return db.query(Usuario).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, cpf: Decimal, nome: Optional[str] = None, login: Optional[str] = None) -> Optional[Usuario]:
        """UPDATE: Atualiza os dados de um usuário existente."""
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if usuario:
            if nome:
                usuario.nome = nome
            if login:
                usuario.login = login
            db.commit()
            db.refresh(usuario)
        return usuario

    @staticmethod
    def delete(db: Session, cpf: Decimal) -> bool:
        """DELETE: Remove um usuário do banco."""
        usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if usuario:
            db.delete(usuario)
            db.commit()
            return True
        return False