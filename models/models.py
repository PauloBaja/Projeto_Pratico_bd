from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import CheckConstraint, Column, Date, Double, Enum, ForeignKeyConstraint, Integer, NUMERIC, Numeric, PrimaryKeyConstraint, REAL, Sequence, SmallInteger, String, Table, UniqueConstraint, VARCHAR
from sqlalchemy.dialects.postgresql import ARRAY, DOMAIN
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class StatusEstudante(str, enum.Enum):
    ATIVO = 'Ativo'
    CANCELADA = 'Cancelada'
    FORMANDO = 'Formando'
    GRADUADO = 'Graduado'


class TipoFormacao(str, enum.Enum):
    GRADUAÇÃO = 'Graduação'
    ESPECIALIZAÇÃO = 'Especialização'
    MESTRADO = 'Mestrado'
    DOUTORADO = 'Doutorado'


class TipoGrau(str, enum.Enum):
    BACHARELADO = 'Bacharelado'
    LICENCIATURA_PLENA = 'Licenciatura Plena'


class TipoJornada(str, enum.Enum):
    _20H = '20h'
    _40H = '40h'
    DE = 'DE'


class TipoNivel(str, enum.Enum):
    GRADUAÇÃO = 'Graduação'
    MESTRADO = 'Mestrado'
    DOUTORADO = 'Doutorado'
    LATO = 'Lato'


class TipoTurno(str, enum.Enum):
    MATUTINO = 'Matutino'
    VESPERTINO = 'Vespertino'
    NOTURNO = 'Noturno'
    TURNO_INDEFINIDO = 'Turno Indefinido'


class Alocacao(Base):
    __tablename__ = 'alocacao'
    __table_args__ = (
        PrimaryKeyConstraint('id_turma', 'id_horario', name='pk_alocacao'),
        UniqueConstraint('id_horario', 'id_sala', name='uq_alocacao'),
        {'schema': 'universidade'}
    )

    id_turma: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_horario: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_sala: Mapped[Optional[int]] = mapped_column(Integer)


class Curso(Base):
    __tablename__ = 'curso'
    __table_args__ = (
        PrimaryKeyConstraint('idcurso', name='curso_pkey'),
        UniqueConstraint('nome', 'turno', 'campus', 'nivel', name='uq_curso'),
        {'schema': 'universidade'}
    )

    idcurso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    turno: Mapped[TipoTurno] = mapped_column(Enum(TipoTurno, values_callable=lambda cls: [member.value for member in cls], name='tipo_turno', schema='universidade'), nullable=False)
    grau: Mapped[Optional[TipoGrau]] = mapped_column(Enum(TipoGrau, values_callable=lambda cls: [member.value for member in cls], name='tipo_grau', schema='universidade'))
    campus: Mapped[Optional[str]] = mapped_column(String(100))
    nivel: Mapped[Optional[TipoNivel]] = mapped_column(Enum(TipoNivel, values_callable=lambda cls: [member.value for member in cls], name='tipo_nivel', schema='universidade'))

    vinculo: Mapped[list['Vinculo']] = relationship('Vinculo', back_populates='curso_')


class Departamento(Base):
    __tablename__ = 'departamento'
    __table_args__ = (
        CheckConstraint('orcamento > 0::double precision', name='ck_orcamento'),
        ForeignKeyConstraint(['chefe'], ['universidade.professor.mat_professor'], ondelete='SET NULL', onupdate='CASCADE', name='fk_chefia'),
        PrimaryKeyConstraint('cod_depto', name='pk_departamento'),
        {'schema': 'universidade'}
    )

    cod_depto: Mapped[str] = mapped_column(String(5), primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    chefe: Mapped[Optional[str]] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'))
    orcamento: Mapped[Optional[float]] = mapped_column(REAL)
    comissal: Mapped[Optional[float]] = mapped_column(Double(53))

    professor_chefe: Mapped[Optional['Professor']] = relationship('Professor', foreign_keys=[chefe], back_populates='departamento_chefe')
    professor_departamento: Mapped[list['Professor']] = relationship('Professor', foreign_keys='[Professor.departamento]', back_populates='departamento_')
    disciplina: Mapped[list['Disciplina']] = relationship('Disciplina', back_populates='departamento')


class Horario(Base):
    __tablename__ = 'horario'
    __table_args__ = (
        PrimaryKeyConstraint('id_horario', name='pk_horario'),
        {'schema': 'universidade'}
    )

    id_horario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dia: Mapped[str] = mapped_column(String(15), nullable=False)
    slot: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class Professor(Base):
    __tablename__ = 'professor'
    __table_args__ = (
        ForeignKeyConstraint(['cpf'], ['universidade.usuario.cpf'], ondelete='SET NULL', onupdate='CASCADE', name='fk_usuario'),
        ForeignKeyConstraint(['departamento'], ['universidade.departamento.cod_depto'], ondelete='SET NULL', onupdate='CASCADE', name='fk_alocacao'),
        PrimaryKeyConstraint('mat_professor', name='pk_professor'),
        UniqueConstraint('cpf', name='professor_cpf_key'),
        {'schema': 'universidade'}
    )

    mat_professor: Mapped[str] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'), primary_key=True)
    cpf: Mapped[Optional[decimal.Decimal]] = mapped_column(DOMAIN('tipo_cpf', NUMERIC(), not_null=False, schema='universidade'))
    departamento: Mapped[Optional[str]] = mapped_column(String(5))
    formacao: Mapped[Optional[TipoFormacao]] = mapped_column(Enum(TipoFormacao, values_callable=lambda cls: [member.value for member in cls], name='tipo_formacao', schema='universidade'))
    data_admissao: Mapped[Optional[datetime.date]] = mapped_column(Date)
    tipo_jornada_trabalho: Mapped[Optional[TipoJornada]] = mapped_column(Enum(TipoJornada, values_callable=lambda cls: [member.value for member in cls], name='tipo_jornada', schema='universidade'))
    salario: Mapped[Optional[float]] = mapped_column(Double(53))

    # CORRIGIDO: back_populates alterado de 'professor' para 'professor_chefe'
    departamento_chefe: Mapped[list['Departamento']] = relationship('Departamento', foreign_keys='[Departamento.chefe]', back_populates='professor_chefe')
    usuario: Mapped[Optional['Usuario']] = relationship('Usuario', back_populates='professor')
    departamento_: Mapped[Optional['Departamento']] = relationship('Departamento', foreign_keys=[departamento], back_populates='professor_departamento')
    plano: Mapped[list['Plano']] = relationship('Plano', back_populates='professor')
    turma: Mapped[list['Turma']] = relationship('Turma', secondary='universidade.leciona', back_populates='professor')


class Projeto(Base):
    __tablename__ = 'projeto'
    __table_args__ = (
        PrimaryKeyConstraint('id_projeto', name='pk_projeto'),
        {'schema': 'universidade'}
    )

    id_projeto: Mapped[int] = mapped_column(Integer, primary_key=True)
    descricao: Mapped[Optional[str]] = mapped_column(String)

    plano: Mapped[list['Plano']] = relationship('Plano', back_populates='projeto')


class Sala(Base):
    __tablename__ = 'sala'
    __table_args__ = (
        PrimaryKeyConstraint('id_sala', name='pk_sala'),
        {'schema': 'universidade'}
    )

    id_sala: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descricao: Mapped[Optional[str]] = mapped_column(String)


class Semestre(Base):
    __tablename__ = 'semestre'
    __table_args__ = (
        PrimaryKeyConstraint('ano', 'semestre', name='pk_semestre'),
        {'schema': 'universidade'}
    )

    ano: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    semestre: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    data_inicio: Mapped[Optional[datetime.date]] = mapped_column(Date)
    data_fom: Mapped[Optional[datetime.date]] = mapped_column(Date)

    turma: Mapped[list['Turma']] = relationship('Turma', back_populates='semestre_')


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = (
        PrimaryKeyConstraint('cpf', name='pk_usuario'),
        UniqueConstraint('login', name='usuario_login_key'),
        {'schema': 'universidade'}
    )

    cpf: Mapped[decimal.Decimal] = mapped_column(DOMAIN('tipo_cpf', NUMERIC(), not_null=False, schema='universidade'), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data_nascimento: Mapped[Optional[datetime.date]] = mapped_column(Date)
    email: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    telefone: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    login: Mapped[Optional[str]] = mapped_column(String(45))
    senha: Mapped[Optional[str]] = mapped_column(String(32))

    professor: Mapped[Optional['Professor']] = relationship('Professor', uselist=False, back_populates='usuario')
    estudante: Mapped[Optional['Estudante']] = relationship('Estudante', uselist=False, back_populates='usuario')


class Disciplina(Base):
    __tablename__ = 'disciplina'
    __table_args__ = (
        CheckConstraint('1 <= creditos AND creditos < 12', name='ck_creditos'),
        ForeignKeyConstraint(['depto_responsavel'], ['universidade.departamento.cod_depto'], ondelete='SET NULL', onupdate='CASCADE', name='fk_responsavel'),
        ForeignKeyConstraint(['pre_req'], ['universidade.disciplina.cod_disc'], ondelete='SET NULL', onupdate='CASCADE', name='fk_pre_req'),
        PrimaryKeyConstraint('cod_disc', name='pk_disciplina'),
        {'schema': 'universidade'}
    )

    cod_disc: Mapped[str] = mapped_column(String(8), primary_key=True)
    nome: Mapped[str] = mapped_column(String(40), nullable=False)
    pre_req: Mapped[Optional[str]] = mapped_column(String(8))
    creditos: Mapped[Optional[int]] = mapped_column(SmallInteger)
    depto_responsavel: Mapped[Optional[str]] = mapped_column(String(5))

    departamento: Mapped[Optional['Departamento']] = relationship('Departamento', back_populates='disciplina')
    disciplina: Mapped[Optional['Disciplina']] = relationship('Disciplina', remote_side=[cod_disc], back_populates='disciplina_reverse')
    disciplina_reverse: Mapped[list['Disciplina']] = relationship('Disciplina', remote_side=[pre_req], back_populates='disciplina')
    turma: Mapped[list['Turma']] = relationship('Turma', back_populates='disciplina')


class Estudante(Base):
    __tablename__ = 'estudante'
    __table_args__ = (
        ForeignKeyConstraint(['cpf'], ['universidade.usuario.cpf'], ondelete='SET NULL', onupdate='CASCADE', name='fk_usuario'),
        PrimaryKeyConstraint('mat_estudante', name='pk_estudante'),
        UniqueConstraint('cpf', name='uq_cpf'),
        {'schema': 'universidade'}
    )

    mat_estudante: Mapped[str] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'), primary_key=True)
    cpf: Mapped[Optional[decimal.Decimal]] = mapped_column(DOMAIN('tipo_cpf', NUMERIC(), not_null=False, schema='universidade'))
    mc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(2, 0))
    ano_ingresso: Mapped[Optional[int]] = mapped_column(Integer)

    usuario: Mapped[Optional['Usuario']] = relationship('Usuario', back_populates='estudante')
    plano: Mapped[list['Plano']] = relationship('Plano', back_populates='estudante')
    vinculo: Mapped[list['Vinculo']] = relationship('Vinculo', back_populates='estudante')
    cursa: Mapped[list['Cursa']] = relationship('Cursa', back_populates='estudante')


class Plano(Base):
    __tablename__ = 'plano'
    __table_args__ = (
        ForeignKeyConstraint(['id_projeto'], ['universidade.projeto.id_projeto'], ondelete='CASCADE', onupdate='CASCADE', name='fk_projeto'),
        ForeignKeyConstraint(['mat_estudante'], ['universidade.estudante.mat_estudante'], ondelete='SET NULL', onupdate='CASCADE', name='fk_mat_estudante'),
        ForeignKeyConstraint(['mat_professor'], ['universidade.professor.mat_professor'], ondelete='SET NULL', onupdate='CASCADE', name='fk_professor'),
        PrimaryKeyConstraint('mat_estudante', 'ano', name='pk_plano'),
        {'schema': 'universidade'}
    )

    mat_estudante: Mapped[str] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'), primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_projeto: Mapped[Optional[int]] = mapped_column(Integer)
    mat_professor: Mapped[Optional[str]] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'))

    projeto: Mapped[Optional['Projeto']] = relationship('Projeto', back_populates='plano')
    estudante: Mapped['Estudante'] = relationship('Estudante', back_populates='plano')
    professor: Mapped[Optional['Professor']] = relationship('Professor', back_populates='plano')


class Turma(Base):
    __tablename__ = 'turma'
    __table_args__ = (
        ForeignKeyConstraint(['ano', 'semestre'], ['universidade.semestre.ano', 'universidade.semestre.semestre'], onupdate='CASCADE', name='fk_semestre'),
        ForeignKeyConstraint(['cod_disc'], ['universidade.disciplina.cod_disc'], ondelete='CASCADE', onupdate='CASCADE', name='fk_disciplina'),
        PrimaryKeyConstraint('id_turma', name='pk_turma'),
        UniqueConstraint('cod_disc', 'numero', 'semestre', 'ano', name='uq_turma'),
        {'schema': 'universidade'}
    )

    id_turma: Mapped[int] = mapped_column(Integer, Sequence('seq_turma', schema='universidade'), primary_key=True, autoincrement=True)
    cod_disc: Mapped[str] = mapped_column(String(8), nullable=False)
    numero: Mapped[Optional[int]] = mapped_column(Integer)
    ano: Mapped[Optional[int]] = mapped_column(SmallInteger)
    semestre: Mapped[Optional[int]] = mapped_column(SmallInteger)

    semestre_: Mapped[Optional['Semestre']] = relationship('Semestre', back_populates='turma')
    disciplina: Mapped['Disciplina'] = relationship('Disciplina', back_populates='turma')
    professor: Mapped[list['Professor']] = relationship('Professor', secondary='universidade.leciona', back_populates='turma')
    cursa: Mapped[list['Cursa']] = relationship('Cursa', back_populates='turma')


class Vinculo(Base):
    __tablename__ = 'vinculo'
    __table_args__ = (
        ForeignKeyConstraint(['curso'], ['universidade.curso.idcurso'], ondelete='SET NULL', onupdate='CASCADE', name='fk_curso'),
        ForeignKeyConstraint(['mat_estudante'], ['universidade.estudante.mat_estudante'], ondelete='SET NULL', onupdate='CASCADE', name='fk_estudabte'),
        PrimaryKeyConstraint('idvinculo', name='vinculo_pkey'),
        {'schema': 'universidade'}
    )

    idvinculo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mat_estudante: Mapped[Optional[str]] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'))
    curso: Mapped[Optional[int]] = mapped_column(Integer)
    data_entrada: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[Optional[StatusEstudante]] = mapped_column(Enum(StatusEstudante, values_callable=lambda cls: [member.value for member in cls], name='status_estudante', schema='universidade'))
    data_saida: Mapped[Optional[datetime.date]] = mapped_column(Date)

    curso_: Mapped[Optional['Curso']] = relationship('Curso', back_populates='vinculo')
    estudante: Mapped[Optional['Estudante']] = relationship('Estudante', back_populates='vinculo')


class Cursa(Base):
    __tablename__ = 'cursa'
    __table_args__ = (
        ForeignKeyConstraint(['id_turma'], ['universidade.turma.id_turma'], ondelete='CASCADE', onupdate='CASCADE', name='fk_turma'),
        ForeignKeyConstraint(['mat_estudante'], ['universidade.estudante.mat_estudante'], ondelete='CASCADE', onupdate='CASCADE', name='fk_estudante'),
        PrimaryKeyConstraint('mat_estudante', 'id_turma', name='pk_cursa'),
        {'schema': 'universidade'}
    )

    mat_estudante: Mapped[str] = mapped_column(DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'), primary_key=True)
    id_turma: Mapped[int] = mapped_column(Integer, primary_key=True)
    nota: Mapped[Optional[float]] = mapped_column(REAL)

    turma: Mapped['Turma'] = relationship('Turma', back_populates='cursa')
    estudante: Mapped['Estudante'] = relationship('Estudante', back_populates='cursa')


t_leciona = Table(
    'leciona', Base.metadata,
    Column('id_turma', Integer, primary_key=True),
    Column('mat_professor', DOMAIN('matricula', VARCHAR(collation='default'), not_null=False, schema='universidade'), primary_key=True),
    ForeignKeyConstraint(['id_turma'], ['universidade.turma.id_turma'], ondelete='CASCADE', onupdate='CASCADE', name='fk_turma'),
    ForeignKeyConstraint(['mat_professor'], ['universidade.professor.mat_professor'], ondelete='CASCADE', onupdate='CASCADE', name='fk_professor'),
    PrimaryKeyConstraint('id_turma', 'mat_professor', name='pk_leciona'),
    schema='universidade'
)