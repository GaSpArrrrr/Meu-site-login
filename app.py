from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Configuração das credenciais via Variável de Ambiente (para segurança no deploy)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_google_sheets_client():
    """Conecta ao Google Sheets usando credenciais de variável de ambiente"""
    try:
        # No deploy, as credenciais estarão na variável de ambiente 'GOOGLE_CREDENTIALS'
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            # Fallback para arquivo local se a variável não existir (para testes locais)
            return gspread.authorize(Credentials.from_service_account_file('credentials.json', scopes=SCOPES))
        
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Erro ao conectar ao Google Sheets: {e}")
        return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'message': 'E-mail é obrigatório'}), 400
        
        client = get_google_sheets_client()
        if not client:
            return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500
        
        # Use o ID da sua planilha convertida aqui
        spreadsheet_id = os.environ.get('SPREADSHEET_ID', '1COGa_Zk9Y5GhldBU6Fxn0O9DFslrPNTlHM4sDZrqfBI')
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.get_worksheet(0)
        
        data_acesso = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        worksheet.append_row([email, data_acesso])
        
        return jsonify({'success': True, 'message': 'Login registrado'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

if __name__ == '__main__':
    # Porta padrão para deploy
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
