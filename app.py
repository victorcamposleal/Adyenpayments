


from flask import Flask, request, jsonify
from openpyxl import Workbook, load_workbook
import os

app = Flask(__name__)
excel_file = "adyen_webhooks.xlsx"

# Crear archivo Excel si no existe
if not os.path.exists(excel_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Webhooks"
    ws.append(["EventCode", "Success", "PSPReference", "MerchantAccount", "Currency", "Amount"])
    wb.save(excel_file)

@app.route('/adyen-webhook', methods=['POST'])
def adyen_webhook():
    data = request.get_json()
    print("Webhook recibido:", data)

    if "notificationItems" in data:
        wb = load_workbook(excel_file)
        ws = wb["Webhooks"]

        for item in data["notificationItems"]:
            notif = item["NotificationRequestItem"]
            ws.append([
                notif.get("eventCode"),
                notif.get("success"),
                notif.get("pspReference"),
                notif.get("merchantAccountCode"),
                notif.get("amount", {}).get("currency"),
                notif.get("amount", {}).get("value")
            ])

        wb.save(excel_file)

    return jsonify({"status": "[accepted]"}), 200

if __name__ == '__main__':
    import os 
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
