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

def show_all():
    DATABASE_URL = os.environ['DATABASE_URL']
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    table_columns = '(name, type)'
    postgres_select_query = f"""SELECT * FROM food"""

    cursor.execute(postgres_select_query)

    record = cursor.fetchall()
    message = "餐廳, 類型"

    for r in record:
        message+= f'{r[0]}, {r[1]}\n'

    cursor.close()
    conn.close()

    return message

def message_preprocess(text):
    text = text.split('\n')
    if text[0] != '存入': return []
    record_list = []
    for line in text[1:]:
        record = (line.split(' ')[0], line.split(' ')[1])
        record_list.append(record)

    return record_list

def insert_data(record_list):
    DATABASE_URL = os.environ['DATABASE_URL']
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    table_columns = '(name, type)'
    postgres_insert_query = f"""INSERT INTO food {table_columns} VALUES (%s,%s)"""

    cursor.executemany(postgres_insert_query, record_list)
    conn.commit()
    
    message = f"成功存入 {cursor.rowcount} 筆資料"
    
    cursor.close()
    conn.close()

    return message

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # ''' Copy user message and reply'''
    # message = TextSendMessage(text=event.message.text) # reply message
    # line_bot_api.reply_message(event.reply_token, message) # send back

    raw_msg = event.message.text

    if raw_msg == 'all':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=show_all())) # send back

    record_list = message_preprocess(raw_msg)
    if len(record_list) == 0:
        message = "輸入格式為:\n存入\n餐廳名字1 類型\n餐廳名字2 類型\n...\n類型有:早餐、午餐、晚餐、飲料、點心"
    else:
        message = insert_data(record_list)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(message)) # send back

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
