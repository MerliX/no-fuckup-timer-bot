import os
import requests
from flask import Flask

app = Flask(__name__)

def setup_webhook():
    bot_token = os.environ.get('BOT_TOKEN')
    heroku_app = os.environ.get('HEROKU_APP')
    requests.post(f'https://api.telegram.org/bot{bot_token}/setWebhook?url=https://{heroku_app}.herokuapp.com/')

setup_webhook()

@app.route('/', methods=['POST'])
def handle_update():
    update = requests.get_json()
    chat_id = update['message']['chat']['id']
    message = "This is a response from the bot"
    bot_token = os.environ.get('BOT_TOKEN')
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}')
    return "ok"

if __name__ == '__main__':
    app.run(port=8000)
