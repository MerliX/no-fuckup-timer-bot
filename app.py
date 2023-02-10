import datetime
import os
import requests
import sqlalchemy
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

import logging

logger = logging.getLogger(__name__)


def setup_webhook():
    bot_token = os.environ.get('BOT_TOKEN')
    bot_url = os.environ.get('BOT_URL')
    requests.post(f'https://api.telegram.org/bot{bot_token}/setWebhook?url={bot_url}')
    logger.info("Bot webhook set")


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    db = SQLAlchemy(app)

    class Failure(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        comment = db.Column(db.String(), nullable=False)
        user = db.Column(db.String(), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

        def __repr__(self):
            return f'<Failure id={self.id} comment={self.comment} user={self.user} created_at={self.created_at}>'

    with app.app_context():
        try:
            db.create_all()
        except sqlalchemy.exc.IntegrityError:
            pass

    setup_webhook()
    @app.route('/bot/', methods=['POST'])
    def handle_update():

        update = request.get_json()
        logger.info(update)
        message = update.get('message')
        if message and message.get('text'):
            command, *comment = message['text'].split()
            chat_id = message['chat']['id']
            response = "Ничего не понятно"
            if command == '/proeb' and comment:
                comment = ' '.join(comment)
                failure = Failure(comment=comment, user=str(message.get('from')))
                db.session.add(failure)
                db.session.commit()
                response = f"Проеб засчитан: '{comment}'"
            elif command == '/proeb':
                response = "Укажи, что именно пошло не так (пример: `/proeb я покакал`)"
            elif command == '/last':
                # Get the latest failure from the database
                latest_failure = Failure.query.order_by(Failure.created_at.desc()).first()
                if latest_failure:
                    time_passed = datetime.datetime.now() - latest_failure.created_at
                    response=f'Минут с последнего проеба: {time_passed.minutes}'

            bot_token = os.environ.get('BOT_TOKEN')
            requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={response}')
        return "ok"

    @app.route('/bot/list/', methods=['GET'])
    def handle_list():
        failures = Failure.query.all()
        return render_template('failures.html', failures=failures)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=8080)
