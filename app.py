import os
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from models import Failure

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)


def setup_webhook():
    bot_token = os.environ.get('BOT_TOKEN')
    bot_url = os.environ.get('BOT_URL')
    requests.post(f'https://api.telegram.org/bot{bot_token}/setWebhook?url={bot_url}')


@app.route('/', methods=['POST'])
def handle_update():
    update = request.get_json()
    message = update.get('message')
    if message and message.get('text'):
        command, *comment = message['text'].split()
        chat_id = message['chat']['id']
        if command == '/failure' and comment:
            comment = ' '.join(comment)
            failure = Failure(comment=comment)
            db.session.add(failure)
            db.session.commit()
            response = f"Failure recorded: '{comment}'"
        else:
            response = "Invalid command or comment"
        bot_token = os.environ.get('BOT_TOKEN')
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={response}')
    return "ok"

if __name__ == '__main__':
    db.create_all()
    setup_webhook()
    app.run(port=8000)
