# TVBOX

Totem de Autoatendimento - TV Box TX9

Sistema de senhas e votação eletrônica desenvolvido na disciplina Tópicos Avançados em Informática II (IFC Rio do Sul, orientação Prof. MEng. Rodrigo Curvêllo).
O projeto transforma uma TV Box em totem funcional para gerenciar filas (senhas normal e prioritária) e realizar votações eletrônicas com controle de voto único por matrícula. Roda em Flask + PostgreSQL com impressão na impressora Epson TM-T20.

Estrutura

app.py - Aplicação Flask
configuracao.py - Configurações (senha admin, banco)
models.py - Gerenciadores (senhas, votação, relatórios)
schema.sql - Estrutura do banco PostgreSQL
requirements.txt - Dependências

Como rodar

Clone o repositório
cd totem-autoatendimento
Ambiente virtual
python3 -m venv venv
source venv/bin/activate
Instale dependências
pip install -r requirements.txt

Configure o PostgreSQL

Crie banco totem_db, usuário totem_usuario e senha totem_pass
sudo -u postgres psql
CREATE DATABASE totem_db;
CREATE USER totem_usuario WITH PASSWORD 'totem_pass';
GRANT ALL PRIVILEGES ON DATABASE totem_db TO totem_usuario;
\q
Execute o schema
psql -h localhost -U totem_usuario -d totem_db -f schema.sql

Inicie o servidor
python3 app.py

Acesse em http://localhost:8000 ou pelo IP da TV Box na rede local.

Configuração da Impressora Epson TM-T20

Detecte o serial USB atual
lpinfo -v | grep usb
Configure no CUPS (substitua o serial se necessário)
sudo lpadmin -p EpsonTM -E -v "usb://EPSON/TM-T20?serial=SEU_SERIAL_AQUI" -m raw
sudo lpadmin -d EpsonTM
sudo cupsenable EpsonTM
sudo cupsaccept EpsonTM
sudo chmod 666 /dev/usb/lp0
Se o serial USB mudar ao reconectar, recrie o dispositivo com o comando acima.

Funcionalidades

Sistema de Senhas
Geração normal/prioritária com impressão automática
Fila em tempo real via navegador
Controle de atendimento
Sistema de Votação
Cadastro com matrícula e nome
Controle de voto único (flag no banco)
Comprovante impresso opcional
Painel Admin
Login: ifcadmin2025
Adicionar/remover candidatos
Reset de senhas e votação
Relatórios

Limitações conhecidas

Wi-Fi não funciona na TV Box TX9, mesmo com drivers instalados
Use cabo Ethernet para estabilidade
Serial USB da impressora pode variar ao reconectar
Reconfigure o CUPS quando necessário
Interface não otimizada para touchscreen
Requer mouse e teclado

Hardware utilizado

TV Box TX9 (Amlogic S905X, 2GB RAM, 16GB eMMC)
Armbian Linux 25.08.0 (kernel 6.12.37)
Impressora térmica Epson TM-T20 (USB)
Monitor HDMI, mouse e teclado

Autor
Magdiel Prestes Rodrigues
Ciência da Computação - IFC Rio do Sul
Orientador: Prof. MEng. Rodrigo Curvêllo
Projeto validado em ambiente real, focado em baixo custo e reutilização de hardware.
