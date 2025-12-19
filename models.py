import psycopg2
from datetime import datetime
import hashlib


class Senha:
    def __init__(
            self,
            id_senha,
            numero,
            prioridade=0,
            status="pendente",
            data_emissao=None,
            servico=None,
            idade=None,
            prior_check=False):
        self.id_senha = id_senha
        self.numero = numero
        self.prioridade = prioridade
        self.status = status
        self.data_emissao = data_emissao or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.servico = servico
        self.idade = idade
        self.prior_check = prior_check

    def to_dict(self):
        return {
            "id_senha": self.id_senha,
            "numero": self.numero,
            "prioridade": self.prioridade,
            "status": self.status,
            "data_emissao": self.data_emissao,
            "servico": self.servico,
            "idade": self.idade,
            "prior_check": self.prior_check
        }


class SenhaManager:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'totem_db',
            'user': 'totem_usuario',
            'password': 'totem_pass'
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def nova_senha(self, prioridade):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            prefixo = "P" if prioridade == 1 else "A"
            cursor.execute(
                "SELECT numero FROM senhas WHERE numero LIKE %s ORDER BY id_senha DESC LIMIT 1",
                (prefixo +
                 '%',
                 ))
            row = cursor.fetchone()
            num = int(row[0][1:]) + 1 if row else 1
            numero = f"{prefixo}{num:03d}"

            data_atual = datetime.now()

            cursor.execute("""
                INSERT INTO senhas (numero, prioridade, status, data_emissao)
                VALUES (%s, %s, 'pendente', %s)
                RETURNING id_senha
            """, (numero, prioridade, data_atual))

            id_senha = cursor.fetchone()[0]
            conn.commit()
            return numero
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def listar_senhas(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_senha, numero, prioridade, status, data_emissao
                FROM senhas
                ORDER BY prioridade DESC, data_emissao ASC
            """)
            rows = cursor.fetchall()
            return [Senha(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None
            ) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def atualizar_status(self, id_senha, status):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE senhas SET status = %s WHERE id_senha = %s", (status, id_senha))
            conn.commit()
        finally:
            cursor.close()
            conn.close()


class VotacaoManager:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'totem_db',
            'user': 'totem_usuario',
            'password': 'totem_pass'
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def registrar_voto(self, enquete_id, candidato_id, aluno_id, ip_hash):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """ INSERT INTO votos (enquete_id, candidato_id, aluno_id, ip_hash) VALUES (%s, %s, %s, %s) """,
                (enquete_id,
                 candidato_id,
                 aluno_id,
                 ip_hash))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def contar_votos(self, enquete_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if enquete_id:
                cursor.execute(
                    "SELECT opcao, COUNT(*) FROM votos WHERE enquete_id = %s GROUP BY opcao",
                    (enquete_id,
                     ))
            else:
                cursor.execute(
                    "SELECT opcao, COUNT(*) FROM votos GROUP BY opcao")
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        finally:
            cursor.close()
            conn.close()

    def total_votos(self, enquete_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if enquete_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM votos WHERE enquete_id = %s", (enquete_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM votos")
            total = cursor.fetchone()[0]
            return total
        finally:
            cursor.close()
            conn.close()

    def listar_todos_votos(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, opcao, data_voto FROM votos ORDER BY data_voto DESC")
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()
            conn.close()
# Gerenciador de alunos - cuida do cadastro e controle de voto


class GerenciadorAluno:
    def __init__(self, config_banco):
        self.config_banco = config_banco

    # Conexão com o banco
    def _conectar(self):
        return psycopg2.connect(**self.config_banco)

    # Cadastra um aluno novo e retorna o ID dele, ou None se matrícula já
    # existe
    def cadastrar(self, matricula, nome_completo):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO alunos (matricula, nome_completo)
                VALUES (%s, %s)
                RETURNING id_aluno
            """, (matricula.strip().upper(), nome_completo.strip().upper()))
            id_aluno = cursor.fetchone()[0]
            conn.commit()
            return id_aluno
        except psycopg2.IntegrityError:
            conn.rollback()
            return None  # Já tem essa matrícula
        finally:
            cursor.close()
            conn.close()

    # Verifica se o aluno já votou
    def ja_votou(self, matricula):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT ja_votou FROM alunos
                WHERE matricula = %s
            """, (matricula.strip().upper(),))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else False
        finally:
            cursor.close()
            conn.close()

    # Marca que o aluno já votou
    def marcar_como_votou(self, matricula):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE alunos SET ja_votou = TRUE
                WHERE matricula = %s
            """, (matricula.strip().upper(),))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    # Busca os dados do aluno pela matrícula
    def buscar_por_matricula(self, matricula):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_aluno, matricula, nome_completo, ja_votou
                FROM alunos WHERE matricula = %s
            """, (matricula.strip().upper(),))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()


# Gerenciador de candidatos - adiciona, remove e lista os da votação
class GerenciadorCandidato:
    def __init__(self, config_banco):
        self.config_banco = config_banco

    def _conectar(self):
        return psycopg2.connect(**self.config_banco)

    # Lista só os candidatos ativos
    def listar_ativos(self):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_candidato, nome, numero
                FROM candidatos
                WHERE ativo = TRUE
                ORDER BY numero
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    # Adiciona um candidato novo
    def adicionar(self, nome, numero):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO candidatos (nome, numero)
                VALUES (%s, %s)
            """, (nome.strip().upper(), numero))
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            conn.rollback()
            return False  # Número duplicado
        finally:
            cursor.close()
            conn.close()

    # Desativa um candidato (não deleta, só marca como inativo)
    def remover(self, id_candidato):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE candidatos SET ativo = FALSE
                WHERE id_candidato = %s
            """, (id_candidato,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()


# Gerenciador de relatórios - faz os relatórios de votação e senhas
class GerenciadorRelatorio:
    def __init__(self, config_banco):
        self.config_banco = config_banco

    def _conectar(self):
        return psycopg2.connect(**self.config_banco)

    # Pega o resultado da votação
    def resultado_votacao(self):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.nome, c.numero, COUNT(v.id) as votos
                FROM candidatos c
                LEFT JOIN votos v ON v.candidato_id = c.id_candidato
                WHERE c.ativo = TRUE
                GROUP BY c.id_candidato, c.nome, c.numero
                ORDER BY votos DESC, c.numero
            """)
            resultados = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM votos")
            total = cursor.fetchone()[0]

            return resultados, total
        finally:
            cursor.close()
            conn.close()

    # Estatísticas básicas das senhas
    def estatisticas_senhas(self):
        conn = self._conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN prioridade = 1 THEN 1 ELSE 0 END) as prioritarias,
                    SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) as pendentes,
                    SUM(CASE WHEN status = 'em_atendimento' THEN 1 ELSE 0 END) as atendendo
                FROM senhas
            """)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
