import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ZALO_ACCESS_TOKEN = "YOUR_ZALO_ACCESS_TOKEN"  # Thay bằng access_token của bạn
RASA_SERVER = "http://localhost:5005/webhooks/rest/webhook"


def send_message_to_zalo(user_id, message):
    url = "https://graph.zalo.me/v2.0/oa/message"
    headers = {"Authorization": f"Bearer {ZALO_ACCESS_TOKEN}",
               "Content-Type": "application/json"}
    data = {
        "recipient": {"user_id": user_id},
        "message": {"text": message}
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


@app.route("/webhook/zalo", methods=["POST"])
def zalo_webhook():
    data = request.json
    user_id = data["sender"]["id"]
    message = data["message"]["text"]

    # Gửi tin nhắn đến Rasa để xử lý
    rasa_response = requests.post(
        RASA_SERVER, json={"sender": user_id, "message": message})
    bot_reply = rasa_response.json()[0]["text"] if rasa_response.json(
    ) else "Xin lỗi, tôi không hiểu."

    # Gửi phản hồi từ Rasa về Zalo
    send_message_to_zalo(user_id, bot_reply)

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(port=5006, debug=True)
