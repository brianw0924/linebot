from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

record = []

# Channel Access Token
line_bot_api = LineBotApi('GVsFuyUq3UEeHkusIBwb0AdQ64oBz4McNa4ZmMmVadrJyRA9Ti3UneuVpNSzjVLbUjwUxZRt6U51/jggniO65EXYPKlB4LemaAuaAqlUNke9JCVNhK5M7w8nhJZwI1e88VMftcrj1hxCi/H1J5XNzgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('00bfaf4c9e147cab87231a495ab3b671')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    if user_msg.split(" ")[0] == "add":
        record.append(user_msg.split(" ")[1:])
        message = TextSendMessage(text=f"add {user_msg.split(" ")[1:]}") # reply message
        line_bot_api.reply_message(event.reply_token, message) # send back
    if user_msg == "check":
        for i in record:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=i)) # send back

    # message = TextSendMessage(text=event.message.text) # reply message
    # line_bot_api.reply_message(event.reply_token, message) # send back

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
