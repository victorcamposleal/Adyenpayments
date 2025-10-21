from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ruta al archivo de credenciales
SERVICE_ACCOUNT_FILE = 'credentials.json'

# ID de la hoja de cálculo de Google Sheets (extraído de la URL)
SPREADSHEET_ID = 'TU_ID_DE_HOJA'  # Reemplaza con tu ID real

# Nombre de la hoja dentro del archivo
SHEET_NAME = 'Sheet1'

# Función para agregar datos a Google Sheets
def append_to_google_sheet(values):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        request = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A2',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [values]}
        )
        request.execute()
        logging.info("Datos agregados a Google Sheets correctamente.")
    except Exception as e:
        logging.error(f"Error al agregar datos a Google Sheets: {e}")

@app.route('/adyen-webhook', methods=['POST'])
def adyen_webhook():
    try:
        data = request.get_json()
        logging.info(f"Webhook recibido: {data}")

        if "notificationItems" in data:
            for item in data["notificationItems"]:
                notif = item["NotificationRequestItem"]

                append_to_google_sheet([
                    notif.get("eventCode"),
                    notif.get("success"),
                    notif.get("pspReference"),
                    notif.get("merchantAccountCode"),
                    notif.get("amount", {}).get("currency"),
                    notif.get("amount", {}).get("value")
                ])

        return jsonify({"status": "[accepted]"}), 200

    except Exception as e:
        logging.error(f"Error procesando webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)