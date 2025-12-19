from flask import Flask, render_template_string, request, jsonify, session, redirect, flash
from datetime import datetime
import hashlib
import psycopg2
import subprocess
import os
from configuracao import SENHA_ADMIN, CONFIG_BANCO, CHAVE_SECRETA
from models import SenhaManager, VotacaoManager, GerenciadorAluno, GerenciadorCandidato, GerenciadorRelatorio

app = Flask(__name__)
app.secret_key = CHAVE_SECRETA

# Instâncias
senha_manager = SenhaManager()
votacao_manager = VotacaoManager()
aluno_manager = GerenciadorAluno(CONFIG_BANCO)
candidato_manager = GerenciadorCandidato(CONFIG_BANCO)
relatorio_manager = GerenciadorRelatorio(CONFIG_BANCO)

# ============ FUNÇÕES DE IMPRESSÃO ============
def imprimir_texto(conteudo, nome_impressora="EpsonTM"):
   #Imprime com comandos ESC/POS binários corretos para Epson TM-T20
    try:
        # Comandos ESC/POS em bytes
        ESC = b'\x1b'
        GS = b'\x1d'
        
        # Comandos de controle
        INIT = ESC + b'@'                      # Inicializa impressora
        CENTER = ESC + b'a\x01'                # Centraliza texto
        LEFT = ESC + b'a\x00'                  # Alinha esquerda
        BOLD_ON = ESC + b'E\x01'               # Negrito ligado
        BOLD_OFF = ESC + b'E\x00'              # Negrito desligado
        CUT_PAPER = GS + b'V\x42\x00'          # Corte parcial
        
        # Converte conteúdo para bytes
        conteudo_bytes = conteudo.encode('utf-8')
        
        # Monta o comando completo
        comando_completo = (
            INIT +
            CENTER + BOLD_ON + b'TOTEM CAC/SUS' + BOLD_OFF + b'\n\n' +
            LEFT + conteudo_bytes + b'\n\n' +
            CUT_PAPER + b'\n\n\n\n\n'
        )
        
        # Salva em arquivo temporário
        arquivo_temp = '/tmp/impressao_totem.bin'
        
        with open(arquivo_temp, 'wb') as f:
            f.write(comando_completo)
        
        # Envia para impressora
        resultado = subprocess.run(
            ['lp', '-d', nome_impressora, '-o', 'raw', arquivo_temp],
            capture_output=True,
            text=True
        )
        
        # Remove arquivo temporário
        os.remove(arquivo_temp)
        
        if resultado.returncode == 0:
            print("Impressão enviada com sucesso para EpsonTM!")
            return True, "Impresso com sucesso!"
        else:
            erro = resultado.stderr
            print(f"Erro lp: {erro}")
            return False, f"Erro de impressão: {erro}"
    
    except Exception as e:
        print(f"Exceção na impressão: {e}")
        return False, str(e)

def formatar_relatorio_texto(resultados, total):
    #Formata relatório para impressão
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
   
    linhas = []
    linhas.append("=" * 42)
    linhas.append(" RELATORIO FINAL DE VOTACAO")
    linhas.append("=" * 42)
    linhas.append(f"Data: {data_hora}")
    linhas.append(f"Total de votos: {total}")
    linhas.append("-" * 42)
    linhas.append("")
   
    for i, (nome, numero, votos) in enumerate(resultados, 1):
        percentual = (votos / total * 100) if total > 0 else 0
        linhas.append(f"{i}. {nome} (No {numero})")
        linhas.append(f"   Votos: {votos} ({percentual:.1f}%)")
        linhas.append("")
   
    linhas.append("=" * 42)
    linhas.append(" Sistema Totem CAC/SUS")
    linhas.append("=" * 42)
   
    return "\n".join(linhas)

def formatar_comprovante_voto(candidato_nome, codigo):
    #Formata comprovante de voto
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
   
    linhas = []
    linhas.append("=" * 42)
    linhas.append(" COMPROVANTE DE VOTO")
    linhas.append("=" * 42)
    linhas.append("")
    linhas.append(f"Candidato: {candidato_nome}")
    linhas.append(f"Codigo: {codigo}")
    linhas.append(f"Data: {data_hora}")
    linhas.append("")
    linhas.append("-" * 42)
    linhas.append(" Obrigado por participar!")
    linhas.append("=" * 42)
   
    return "\n".join(linhas)

def formatar_senha(numero, tipo, data_hora):
    #Formata ticket de senha
    linhas = []
    linhas.append("=" * 42)
    linhas.append(" SENHA DE ATENDIMENTO")
    linhas.append("=" * 42)
    linhas.append("")
    linhas.append(f" SENHA: {numero}")
    linhas.append(f" Tipo: {tipo}")
    linhas.append(f" Data: {data_hora}")
    linhas.append("")
    linhas.append("-" * 42)
    linhas.append(" Aguarde ser chamado")
    linhas.append("=" * 42)
   
    return "\n".join(linhas)

# ============ DECORATOR ============
def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            flash("Acesso negado. Faça login como admin.")
            return redirect('/admin_login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ============ TEMPLATES ============
MENU_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Totem CAC/SUS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f4f4f4; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 10px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; width: 100%; border: 1px solid #ddd; }
        h1 { text-align: center; color: #333; margin-bottom: 40px; font-size: 2em; }
        .menu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }
        .menu-btn { background: #555; color: white; border: none; padding: 30px 20px; border-radius: 5px; font-size: 1.1em; font-weight: bold; cursor: pointer; transition: all 0.3s; text-align: center; }
        .menu-btn:hover { background: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>TOTEM CAC/SUS</h1>
        <p style="text-align: center; color: #666; margin-bottom: 20px;">Escolha uma opção:</p>
        <div class="menu-grid">
            <button class="menu-btn" onclick="location.href='/senhas'">SISTEMA DE SENHAS</button>
            <button class="menu-btn" onclick="location.href='/cadastro_aluno'">SISTEMA DE VOTAÇÃO</button>
            <button class="menu-btn" onclick="location.href='/admin_login'">ÁREA ADMIN</button>
            <button class="menu-btn" onclick="alert('Sistema OK!')">TESTE</button>
        </div>
    </div>
</body>
</html>
'''

SENHAS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Senhas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f4f4f4; min-height: 100vh; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #ddd; }
        h1 { color: #333; }
        .btn { background: #555; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 1em; font-weight: bold; cursor: pointer; transition: all 0.3s; }
        .btn:hover { background: #333; }
        .btn-voltar { background: #888; }
        .actions { background: white; padding: 30px; border-radius: 5px; margin-bottom: 20px; display: flex; gap: 20px; justify-content: center; border: 1px solid #ddd; }
        .btn-normal { background: #555; }
        .btn-priority { background: #333; }
        .fila { background: white; padding: 20px; border-radius: 5px; border: 1px solid #ddd; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #555; color: white; }
        tr:hover { background: #f5f5f5; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
        .modal-content { background: white; padding: 40px; border-radius: 5px; text-align: center; max-width: 400px; border: 1px solid #ddd; }
        .senha-display { font-size: 3em; font-weight: bold; color: #333; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SISTEMA DE SENHAS</h1>
        <button class="btn btn-voltar" onclick="location.href='/'">VOLTAR</button>
    </div>
    <div class="actions">
        <button class="btn btn-normal" onclick="gerarSenha(0)">SENHA NORMAL</button>
        <button class="btn btn-priority" onclick="gerarSenha(1)">SENHA PRIORITÁRIA</button>
    </div>
    <div class="fila">
        <h2 style="margin-bottom: 20px; color: #333;">Fila de Atendimento</h2>
        <table>
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Tipo</th>
                    <th>Status</th>
                    <th>Data/Hora</th>
                    <th>Ação</th>
                </tr>
            </thead>
            <tbody>
                {% for s in senhas %}
                <tr>
                    <td><strong>{{ s.numero }}</strong></td>
                    <td>{{ 'Prioritária' if s.prioridade else 'Normal' }}</td>
                    <td>{{ s.status.replace('_', ' ').upper() }}</td>
                    <td>{{ s.data_emissao }}</td>
                    <td>
                        {% if s.status == 'pendente' %}
                        <button class="btn" style="padding: 8px 15px; font-size: 0.9em;" onclick="atenderSenha({{ s.id_senha }})">ATENDER</button>
                        {% else %}
                        -
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <div id="modalSenha" class="modal">
        <div class="modal-content">
            <h2>SENHA GERADA</h2>
            <div class="senha-display" id="senhaNumero"></div>
            <p>Imprimindo...</p>
            <button class="btn" onclick="fecharModal()">FECHAR</button>
        </div>
    </div>
    <script>
        function gerarSenha(prioridade) {
            fetch('/nova_senha', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prioridade: prioridade})
            })
            .then(r => r.json())
            .then(data => {
                if(data.status === 'criada') {
                    document.getElementById('senhaNumero').innerText = data.numero;
                    document.getElementById('modalSenha').style.display = 'flex';
                    setTimeout(() => location.reload(), 3000);
                }
            });
        }
        function atenderSenha(id) {
            fetch('/atender', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(() => location.reload());
        }
        function fecharModal() {
            document.getElementById('modalSenha').style.display = 'none';
            location.reload();
        }
    </script>
</body>
</html>
'''

VOTACAO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sistema de Votação</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f4f4f4; min-height: 100vh; padding: 20px; }
.header { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #ddd; }
h1 { color: #333; }
.btn { background: #555; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 1em; font-weight: bold; cursor: pointer; transition: all 0.3s; }
.btn:hover { background: #333; }
.btn-voltar { background: #888; }
.votacao-area { background: white; padding: 40px; border-radius: 5px; text-align: center; border: 1px solid #ddd; }
.opcoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
.opcao-btn { padding: 40px 20px; font-size: 1.2em; background: #555; }
.modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
.modal-content { background: white; padding: 40px; border-radius: 5px; text-align: center; max-width: 400px; border: 1px solid #ddd; }
.codigo-display { font-size: 1.5em; font-weight: bold; color: #333; margin: 20px 0; padding: 20px; background: #f4f4f4; border-radius: 5px; border: 1px solid #ddd; }
</style>
</head>
<body>
<div class="header">
    <h1>SISTEMA DE VOTAÇÃO</h1>
    <button class="btn btn-voltar" onclick="location.href='/'">VOLTAR</button>
</div>
<div class="votacao-area">
    <h2 style="color: #333; margin-bottom: 30px;">Escolha seu candidato:</h2>
    <div class="opcoes">
        {% for cand in candidatos %}
        <button class="btn opcao-btn" onclick="votar({{ cand[0] }}, '{{ cand[1] }}')">{{ cand[1] }}<br>(Nº {{ cand[2] }})</button>
        {% endfor %}
    </div>
</div>
<div id="modalVoto" class="modal">
    <div class="modal-content">
        <h2>VOTO REGISTRADO</h2>
        <p style="margin: 20px 0;">Candidato: <strong id="opcaoEscolhida"></strong></p>
        <p>Código de confirmação:</p>
        <div class="codigo-display" id="codigoVoto"></div>
        <button class="btn" onclick="imprimirComprovante()">IMPRIMIR COMPROVANTE</button>
        <button class="btn" style="background: #666; margin-left: 10px;" onclick="location.href='/'">FINALIZAR</button>
    </div>
</div>
<script>
let candidatoNomeGlobal = '';
function votar(id, nome) {
    candidatoNomeGlobal = nome;
    fetch('/registrar_voto', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({candidato_id: id})
    })
    .then(r => r.json())
    .then(data => {
        if(data.status === 'registrado') {
            document.getElementById('opcaoEscolhida').innerText = nome;
            document.getElementById('codigoVoto').innerText = data.codigo;
            document.getElementById('modalVoto').style.display = 'flex';
        } else {
            alert(data.msg);
            location.href = '/';
        }
    });
}
function imprimirComprovante() {
    const codigo = document.getElementById('codigoVoto').innerText;
    fetch('/imprimir_comprovante', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            candidato_nome: candidatoNomeGlobal,
            codigo: codigo
        })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.msg);
    });
}
</script>
</body>
</html>
'''

ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login Admin</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f4f4f4; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
.container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
h1 { text-align: center; color: #333; margin-bottom: 30px; }
input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
button { width: 100%; padding: 15px; background: #555; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; }
button:hover { background: #333; }
.erro { color: red; margin-top: 10px; }
</style>
</head>
<body>
<div class="container">
    <h1>LOGIN ADMIN</h1>
    <form method="POST">
        <input type="password" name="password" placeholder="Senha" required>
        <button type="submit">ENTRAR</button>
    </form>
    {% with messages = get_flashed_messages() %}
    {% if messages %}
    <p class="erro">{{ messages[0] }}</p>
    {% endif %}
    {% endwith %}
    <br>
    <a href="/" style="display: block; text-align: center;">Voltar ao Menu</a>
</div>
</body>
</html>
'''

CADASTRO_ALUNO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cadastro Aluno</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f4f4f4; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
.container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
h1 { text-align: center; color: #333; margin-bottom: 30px; }
input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
button { width: 100%; padding: 15px; background: #555; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; margin-top: 10px; }
button:hover { background: #333; }
.erro { color: red; margin-top: 10px; }
</style>
</head>
<body>
<div class="container">
    <h1>CADASTRO PARA VOTAR</h1>
    <p style="text-align: center; margin-bottom: 20px;">Preencha seus dados para votar</p>
    <form method="POST">
        <input type="text" name="matricula" placeholder="Matrícula" required>
        <input type="text" name="nome_completo" placeholder="Nome Completo" required>
        <button type="submit">CADASTRAR E VOTAR</button>
    </form>
    {% with messages = get_flashed_messages() %}
    {% if messages %}
    <p class="erro">{{ messages[0] }}</p>
    {% endif %}
    {% endwith %}
    <br>
    <a href="/" style="display: block; text-align: center;">Voltar ao Menu</a>
</div>
</body>
</html>
'''

ADMIN_DASH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Dashboard Admin</title>
<style>
body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
.container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
h1, h2 { color: #333; }
form { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 5px; }
input { width: calc(50% - 10px); padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
button { padding: 10px 20px; background: #555; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
button:hover { background: #333; }
ul { list-style: none; padding: 0; }
li { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
.sucesso { color: green; }
.erro { color: red; }
</style>
</head>
<body>
<div class="container">
    <h1>DASHBOARD ADMIN</h1>
   
    <h2>Gerenciar Candidatos</h2>
    <form method="POST" action="/admin/adicionar_candidato">
        <input type="text" name="nome" placeholder="Nome do Candidato" required>
        <input type="number" name="numero" placeholder="Número" required>
        <button type="submit">ADICIONAR CANDIDATO</button>
    </form>
   
    <h3>Candidatos Ativos:</h3>
    <ul>
    {% for cand in candidatos %}
        <li>
            <span><strong>{{ cand[1] }}</strong> (Nº {{ cand[2] }})</span>
            <a href="/admin/remover_candidato/{{ cand[0] }}" style="color: red;">Remover</a>
        </li>
    {% endfor %}
    </ul>
   
    <h2>Ações do Sistema</h2>
    <button onclick="if(confirm('Resetar todas as senhas?')) location.href='/admin/reset_senhas'">RESET SENHAS</button>
    <button onclick="if(confirm('Resetar toda a votação?')) location.href='/admin/reset_votacao'">RESET VOTAÇÃO</button>
    <button onclick="location.href='/admin/relatorio'">VER RELATÓRIO FINAL</button>
   
    <br><br>
    <a href="/logout">Logout</a> | <a href="/">Menu Principal</a>
   
    {% with messages = get_flashed_messages() %}
    {% if messages %}
    <p class="sucesso">{{ messages[0] }}</p>
    {% endif %}
    {% endwith %}
</div>
</body>
</html>
'''

RELATORIO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Final</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; }
.container { max-width: 800px; margin: 0 auto; }
h1 { text-align: center; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { padding: 15px; text-align: left; border: 1px solid #ddd; }
th { background: #555; color: white; }
tr:hover { background: #f5f5f5; }
button { padding: 10px 20px; background: #555; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
button:hover { background: #333; }
@media print {
    .no-print { display: none; }
}
</style>
</head>
<body>
<div class="container">
    <h1>RELATÓRIO FINAL DE VOTAÇÃO</h1>
    <p><strong>Total de votos:</strong> {{ total }}</p>
    <p><strong>Data:</strong> {{ data }}</p>
   
    <table>
        <tr>
            <th>Posição</th>
            <th>Candidato</th>
            <th>Número</th>
            <th>Votos</th>
            <th>Percentual</th>
        </tr>
        {% for res in resultados %}
        <tr>
            <td>{{ loop.index }}º</td>
            <td>{{ res[0] }}</td>
            <td>{{ res[1] }}</td>
            <td>{{ res[2] }}</td>
            <td>{{ "%.2f"|format((res[2] / total * 100) if total > 0 else 0) }}%</td>
        </tr>
        {% endfor %}
    </table>
   
    <div class="no-print">
        <button onclick="location.href='/admin/imprimir_relatorio'">IMPRIMIR NA EPSON</button>
        <button onclick="window.print()"> IMPRIMIR (Browser)</button>
        <button onclick="location.href='/admin'">VOLTAR</button>
    </div>
   
    {% with messages = get_flashed_messages() %}
    {% if messages %}
    <p style="color: green;">{{ messages[0] }}</p>
    {% endif %}
    {% endwith %}
</div>
</body>
</html>
'''

# ============ ROTAS ============
@app.route('/')
def menu():
    return render_template_string(MENU_TEMPLATE)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == SENHA_ADMIN:
            session['admin'] = True
            return redirect('/admin')
        flash("Senha incorreta.")
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin')
@admin_required
def admin():
    candidatos = candidato_manager.listar_ativos()
    return render_template_string(ADMIN_DASH_TEMPLATE, candidatos=candidatos)

@app.route('/admin/adicionar_candidato', methods=['POST'])
@admin_required
def adicionar_candidato():
    nome = request.form['nome']
    numero = int(request.form['numero'])
    if candidato_manager.adicionar(nome, numero):
        flash("Candidato adicionado com sucesso!")
    else:
        flash("Número já existe.")
    return redirect('/admin')

@app.route('/admin/remover_candidato/<int:id_candidato>')
@admin_required
def remover_candidato(id_candidato):
    candidato_manager.remover(id_candidato)
    flash("Candidato removido.")
    return redirect('/admin')

@app.route('/admin/reset_senhas')
@admin_required
def reset_senhas():
    conn = psycopg2.connect(**CONFIG_BANCO)
    cur = conn.cursor()
    try:
        cur.execute("TRUNCATE senhas RESTART IDENTITY;")
        conn.commit()
        flash("Sistema de senhas resetado!")
    except Exception as e:
        flash(f"Erro: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect('/admin')

@app.route('/admin/reset_votacao')
@admin_required
def reset_votacao():
    conn = psycopg2.connect(**CONFIG_BANCO)
    cur = conn.cursor()
    try:
        cur.execute("UPDATE alunos SET ja_votou = FALSE;")
        cur.execute("TRUNCATE votos RESTART IDENTITY;")
        conn.commit()
        flash("Votação resetada com sucesso!")
    except Exception as e:
        flash(f"Erro: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect('/admin')

@app.route('/admin/relatorio')
@admin_required
def admin_relatorio():
    resultados, total = relatorio_manager.resultado_votacao()
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return render_template_string(RELATORIO_TEMPLATE, resultados=resultados, total=total, data=data)

@app.route('/admin/imprimir_relatorio')
@admin_required
def imprimir_relatorio():
    resultados, total = relatorio_manager.resultado_votacao()
    conteudo = formatar_relatorio_texto(resultados, total)
    sucesso, msg = imprimir_texto(conteudo)
    flash(msg)
    return redirect('/admin/relatorio')

@app.route('/cadastro_aluno', methods=['GET', 'POST'])
def cadastro_aluno():
    if request.method == 'POST':
        matricula = request.form['matricula']
        nome_completo = request.form['nome_completo']
        
        if aluno_manager.ja_votou(matricula):
            flash("Esta matrícula já votou!")
            return render_template_string(CADASTRO_ALUNO_TEMPLATE)
        
        id_aluno = aluno_manager.cadastrar(matricula, nome_completo)
        if id_aluno or aluno_manager.buscar_por_matricula(matricula):
            session['matricula'] = matricula
            return redirect('/votacao')
        else:
            flash("Erro ao cadastrar. Tente novamente.")
    
    return render_template_string(CADASTRO_ALUNO_TEMPLATE)

@app.route('/votacao')
def votacao():
    if 'matricula' not in session:
        return redirect('/cadastro_aluno')
    
    matricula = session['matricula']
    if aluno_manager.ja_votou(matricula):
        flash("Você já votou!")
        session.clear()
        return redirect('/')
    
    candidatos = candidato_manager.listar_ativos()
    return render_template_string(VOTACAO_TEMPLATE, candidatos=candidatos)

@app.route('/registrar_voto', methods=['POST'])
def registrar_voto():
    if 'matricula' not in session:
        return jsonify({"status": "erro", "msg": "Cadastro requerido"}), 401
    
    matricula = session['matricula']
    if aluno_manager.ja_votou(matricula):
        return jsonify({"status": "erro", "msg": "Você já votou"}), 400
    
    aluno = aluno_manager.buscar_por_matricula(matricula)
    if not aluno:
        return jsonify({"status": "erro", "msg": "Aluno não encontrado"}), 404
    
    dados = request.get_json()
    candidato_id = dados.get('candidato_id')
    ip_hash = hashlib.sha256(request.remote_addr.encode()).hexdigest()
    
    try:
        votacao_manager.registrar_voto(1, candidato_id, aluno[0], ip_hash)
        aluno_manager.marcar_como_votou(matricula)
        session.clear()
        codigo = "V" + datetime.now().strftime("%Y%m%d%H%M%S")
        return jsonify({"status": "registrado", "codigo": codigo})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

@app.route('/imprimir_comprovante', methods=['POST'])
def imprimir_comprovante():
    dados = request.get_json()
    candidato_nome = dados.get('candidato_nome')
    codigo = dados.get('codigo')
    conteudo = formatar_comprovante_voto(candidato_nome, codigo)
    sucesso, msg = imprimir_texto(conteudo)
    return jsonify({"msg": msg})

@app.route('/senhas')
def senhas():
    lista_senhas = senha_manager.listar_senhas()
    return render_template_string(SENHAS_TEMPLATE, senhas=lista_senhas)

@app.route('/nova_senha', methods=['POST'])
def nova_senha():
    try:
        dados = request.get_json()
        prioridade = int(dados.get('prioridade', 0))
        numero = senha_manager.nova_senha(prioridade)
        
        # Imprime a senha automaticamente
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo = "Prioritária" if prioridade else "Normal"
        conteudo = formatar_senha(numero, tipo, data_hora)
        imprimir_texto(conteudo)
        
        return jsonify({"status": "criada", "numero": numero})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

@app.route('/atender', methods=['POST'])
def atender():
    try:
        dados = request.get_json()
        id_senha = int(dados.get('id'))
        senha_manager.atualizar_status(id_senha, "em_atendimento")
        return jsonify({"status": "atendido"})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
