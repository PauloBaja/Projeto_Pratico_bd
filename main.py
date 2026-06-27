# main.py
from decimal import Decimal
from config.database import SessionLocal
from repositories.usuario_repository import UsuarioRepository

def rodar_teste_crud():
    # 1. Abre a sessão com o banco
    db = SessionLocal()
    
    print("🔄 Testando o CRUD de Usuários...")
    cpf_teste = Decimal("1234567890123")
    
    try:
        # Limpeza prévia para o teste poder rodar repetidas vezes
        UsuarioRepository.delete(db, cpf_teste)
        
        # C - Create
        user = UsuarioRepository.create(db, nome="Paulo Medeiros", cpf=cpf_teste, login="paulo_baja", senha="123")
        print(f"✅ [CREATE] Usuário criado com sucesso: {user.nome}")
        
        # R - Read
        buscado = UsuarioRepository.get_by_cpf(db, cpf_teste)
        print(f"✅ [READ] Usuário buscado no banco: {buscado.nome} (Login: {buscado.login})")
        
        # U - Update
        atualizado = UsuarioRepository.update(db, cpf_teste, nome="Paulo B. Medeiros")
        print(f"✅ [UPDATE] Nome atualizado para: {atualizado.nome}")
        
        # D - Delete
        removido = UsuarioRepository.delete(db, cpf_teste)
        if removido:
            print("✅ [DELETE] Usuário de teste removido com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro durante o teste do CRUD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rodar_teste_crud()