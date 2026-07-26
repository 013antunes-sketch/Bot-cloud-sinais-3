IQ Cloud Signals V2

Sistema de agendamento de até 30 sinais por planilha CSV.


Formato da planilha

Colunas obrigatórias:


ID, DATA, HORA, ATIVO, DIREÇÃO, EXPIRAÇÃO, VALOR


Exemplo:


1,26/07/2026,14:35:00,EUR/USD,CALL,1,R$10


Instalação

python -m venv .venv

Linux/VPS:


source .venv/bin/activate

Windows:


.venv\Scripts\activate

Instalar:


pip install -r requirements.txt

Executar:


uvicorn server:app --host 0.0.0.0 --port 8000

Acessar:
http://localhost:8000


Observação

Esta versão importa, organiza, agenda e gerencia sinais. Ela não envia ordens reais automaticamente à IQ Option. A camada de execução deve usar uma integração compatível e autorizada pela plataforma.

