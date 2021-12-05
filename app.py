import os
import psycopg2

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

line_bot_api = LineBotApi('GVsFuyUq3UEeHkusIBwb0AdQ64oBz4McNa4ZmMmVadrJyRA9Ti3UneuVpNSzjVLbUjwUxZRt6U51/jggniO65EXYPKlB4LemaAuaAqlUNke9JCVNhK5M7w8nhJZwI1e88VMftcrj1hxCi/H1J5XNzgdB04t89/1O/w1cDnyilFU=')
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

def insert_data(record):
    DATABASE_URL = os.environ('DATABASE_URL')
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    table_columns = '(name, type)'
    postgres_insert_query = f"""INSERT INTO food {table_columns} VALUES (%s,%s)"""

    cursor.execute(postgres_insert_query, record)
    conn.cimmit()

    message = f"成功存入餐廳: {record[0]} | 類型: {record[1]}"

    print(message)

    cursor.close()
    conn.close()

    return message

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # raw_msg = event.message.text
    # food_name = raw_msg.split(' ')[0]
    # type_name = raw_msg.split(' ')[1]
    # record = (food_name, type_name)
    # # if type_name not in ['早餐','午餐','晚餐','飲料','點心']:
    # #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入:[餐廳名字] [空格] [類型(早餐,午餐,晚餐,飲料,點心)]')) # send back
    # # else:
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=insert_data(record)) # send back

    message = TextSendMessage(text=event.message.text) # reply message
    line_bot_api.reply_message(event.reply_token, message) # send back

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
