CREATE SCHEMA universidade;

CREATE DOMAIN universidade.matricula AS VARCHAR(7);

CREATE DOMAIN universidade.tipo_cpf AS NUMERIC(13);

CREATE TABLE universidade.usuario(
	cpf universidade.tipo_cpf,
	nome	VARCHAR(100) NOT NULL,
	data_nascimento DATE,
	email VARCHAR[],
	telefone VARCHAR[],
	login VARCHAR(45) UNIQUE,
	senha VARCHAR(32),
	CONSTRAINT pk_usuario PRIMARY KEY (cpf)
);

CREATE TYPE universidade.tipo_jornada AS ENUM ('20h', '40h', 'DE');
CREATE TYPE universidade.tipo_formacao AS ENUM ('Graduação', 'Especialização', 'Mestrado', 'Doutorado');

CREATE TABLE universidade.professor(
	mat_professor universidade.matricula,
	cpf  universidade.tipo_cpf UNIQUE,
	departamento VARCHAR(5),
	formacao universidade.tipo_formacao,
	data_admissao DATE,
	tipo_jornada_trabalho universidade.tipo_jornada,
	salario FLOAT,
	CONSTRAINT pk_professor PRIMARY KEY(mat_professor),
	CONSTRAINT fk_usuario FOREIGN KEY (cpf) REFERENCES universidade.usuario(cpf)
	ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE universidade.departamento(
	cod_depto VARCHAR(5),
	nome VARCHAR(50) NOT NULL,
	chefe universidade.matricula,
	orcamento REAL CONSTRAINT ck_orcamento CHECK(orcamento > 0),
	comissal FLOAT,
	CONSTRAINT pk_departamento PRIMARY KEY(cod_depto)
);

ALTER TABLE universidade.professor ADD 
CONSTRAINT fk_alocacao FOREIGN KEY (departamento) REFERENCES universidade.departamento(cod_depto)
ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE universidade.departamento ADD 
CONSTRAINT fk_chefia FOREIGN KEY (chefe) REFERENCES universidade.professor(mat_professor)
ON DELETE SET NULL ON UPDATE CASCADE;

CREATE TYPE universidade.tipo_grau AS ENUM ('Bacharelado', 'Licenciatura Plena');
CREATE TYPE universidade.tipo_nivel AS ENUM ('Graduação', 'Mestrado', 'Doutorado', 'Lato');
CREATE TYPE universidade.tipo_turno AS ENUM ('Matutino', 'Vespertino', 'Noturno', 'Turno Indefinido');

CREATE TABLE universidade.curso(
	idCurso SERIAL PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	grau universidade.tipo_grau,
	turno universidade.tipo_turno NOT NULL,
	campus VARCHAR(100),
	nivel universidade.tipo_nivel,
	CONSTRAINT uq_curso UNIQUE(nome, turno, campus, nivel)

);

CREATE TYPE universidade.status_estudante AS ENUM ('Ativo', 'Cancelada', 'Formando', 'Graduado');

CREATE TABLE universidade.estudante(
	mat_estudante universidade.matricula,
	cpf  universidade.tipo_cpf ,
	MC DECIMAL(2),
	ano_ingresso INT,

	CONSTRAINT pk_estudante PRIMARY KEY(mat_estudante),
	CONSTRAINT fk_usuario FOREIGN KEY (cpf) REFERENCES universidade.usuario(cpf)
	ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT uq_cpf UNIQUE(cpf)
	
);

CREATE TABLE universidade.vinculo(
	idVinculo SERIAL PRIMARY KEY,
	mat_estudante universidade.matricula,
	curso INT,
	data_entrada DATE,
	status universidade.status_estudante,
	data_saida DATE,
	CONSTRAINT fk_curso FOREIGN KEY (curso) REFERENCES universidade.curso(idCurso)
	ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT fk_estudabte FOREIGN KEY (mat_estudante) REFERENCES universidade.estudante(mat_estudante)
	ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE universidade.projeto(
	id_projeto INT,
	descricao VARCHAR,
	CONSTRAINT pk_projeto PRIMARY KEY(id_projeto)
);

CREATE TABLE universidade.plano(
	id_projeto INT,
	mat_professor universidade.matricula,
	mat_estudante universidade.matricula,
	ano INT,
	CONSTRAINT pk_plano PRIMARY KEY(mat_estudante, ano),
	CONSTRAINT fk_projeto FOREIGN KEY (id_projeto) REFERENCES universidade.projeto(id_projeto) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_professor FOREIGN KEY (mat_professor) REFERENCES universidade.professor(mat_professor) ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT fk_mat_estudante FOREIGN KEY (mat_estudante) REFERENCES universidade.estudante(mat_estudante) ON DELETE SET NULL ON UPDATE CASCADE
);



CREATE TABLE universidade.disciplina(
	cod_disc VARCHAR(8),
	nome	VARCHAR(40) NOT NULL,
	pre_req VARCHAR(8),
	creditos SMALLINT CONSTRAINT  ck_creditos CHECK (1<=creditos AND creditos < 12),
	depto_responsavel VARCHAR(5),
	CONSTRAINT pk_disciplina PRIMARY KEY (cod_disc),
	CONSTRAINT fk_pre_req FOREIGN KEY(pre_req) REFERENCES universidade.disciplina(cod_disc)
	ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT fk_responsavel FOREIGN KEY(depto_responsavel) REFERENCES universidade.departamento(cod_depto)
	ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE SEQUENCE universidade.seq_turma INCREMENT 1 START 1;

CREATE TABLE universidade.semestre(
	ano SMALLINT,
	semestre SMALLINT,
	data_inicio DATE,
	data_fom DATE,
	CONSTRAINT pk_semestre PRIMARY KEY (ano, semestre)
);

CREATE TABLE universidade.sala(
	id_sala SERIAL,
	descricao VARCHAR,
	CONSTRAINT pk_sala PRIMARY KEY (id_sala)
);


CREATE TABLE universidade.horario(
	id_horario SERIAL,
	dia VARCHAR(15) NOT NULL,
	slot  SMALLINT NOT NULL,
	CONSTRAINT pk_horario PRIMARY KEY (id_horario)
);


CREATE TABLE universidade.turma(
	id_turma INT DEFAULT nextval('universidade.seq_turma'),
	cod_disc VARCHAR(8) NOT NULL,
	numero INT,
	ano SMALLINT,
	semestre SMALLINT,
	CONSTRAINT pk_turma PRIMARY KEY(id_turma),
	CONSTRAINT uq_turma UNIQUE(cod_disc, numero, semestre, ano),
	CONSTRAINT fk_disciplina FOREIGN KEY(cod_disc) REFERENCES universidade.disciplina(cod_disc)
	ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_semestre FOREIGN KEY(ano, semestre) REFERENCES universidade.semestre(ano,semestre)
	ON DELETE NO ACTION ON UPDATE CASCADE
);

CREATE TABLE universidade.leciona(
	id_turma INT NOT NULL,
	mat_professor universidade.matricula NOT NULL,
	CONSTRAINT pk_leciona PRIMARY KEY (id_turma, mat_professor),
	CONSTRAINT fk_turma FOREIGN KEY (id_turma) REFERENCES universidade.turma(id_turma) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_professor FOREIGN KEY (mat_professor) REFERENCES universidade.professor(mat_professor) ON DELETE  CASCADE ON UPDATE CASCADE
);

CREATE TABLE universidade.alocacao(
	id_turma INT,
	id_horario INT,
	id_sala INT,
	CONSTRAINT pk_alocacao PRIMARY KEY (id_turma, id_horario),
	CONSTRAINT uq_alocacao UNIQUE(id_horario, id_sala)
);

CREATE TABLE universidade.cursa(
	mat_estudante universidade.matricula,
	id_turma INT,
	nota	REAL,
	CONSTRAINT pk_cursa PRIMARY KEY(mat_estudante, id_turma),
	CONSTRAINT fk_turma FOREIGN KEY(id_turma) REFERENCES universidade.turma(id_turma)
	ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_estudante FOREIGN KEY(mat_estudante) REFERENCES universidade.estudante(mat_estudante)
	ON DELETE CASCADE ON UPDATE CASCADE
);
