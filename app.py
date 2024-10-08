import datetime
import os
import requests
import sqlalchemy
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import ast
import logging

logger = logging.getLogger(__name__)


def setup_webhook():
    bot_token = os.environ.get('BOT_TOKEN')
    bot_url = os.environ.get('BOT_URL')
    requests.post(f'https://api.telegram.org/bot{bot_token}/setWebhook?url={bot_url}')
    logger.info("Bot webhook set")


def convert_timedelta_to_russian_string(td: datetime.timedelta):
    days, remainder = divmod(td.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = []
    if int(days) > 0:
        result.append(f"{int(days)} день(ей)")
    if int(hours) > 0:
        result.append(f"{int(hours)} часа(ов)")
    if int(minutes) > 0:
        result.append(f"{int(minutes)} минут(ы)")
    if not result:
        return "0 минут"
    return " ".join(result)


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
            return f'{self.user} {self.created_at}: {self.comment}'

        @property
        def user_dict(self):
            return ast.literal_eval(self.user)

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
            response = f"Ничего не понятно (команда {command})"
            latest_failure = Failure.query.order_by(Failure.created_at.desc()).first()
            time_passed = datetime.timedelta(0)
            if latest_failure:
                time_passed = datetime.datetime.now() - latest_failure.created_at
            if command in ('/proeb', '/proeb@badbartimerbot') and comment:
                comment = ' '.join(comment)
                failure = Failure(comment=comment, user=str(message.get('from')))
                db.session.add(failure)
                db.session.commit()

                response = f"Проеб засчитан: '{comment}'\nПродержались: {convert_timedelta_to_russian_string(time_passed)}"
            elif command in ('/proeb', '/proeb@badbartimerbot'):
                response = "Укажи, что именно пошло не так (пример: `/proeb я покакал`)"
            elif command in ('/last', '/last@badbartimerbot'):
                # Get the latest failure from the database
                if latest_failure:
                    response=f'Без проеба: {convert_timedelta_to_russian_string(time_passed)}'

            bot_token = os.environ.get('BOT_TOKEN')
            requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={response}')
        return "ok"

    @app.route('/bot/list/', methods=['GET'])
    def handle_list():
        failures = Failure.query.order_by(Failure.created_at.desc()).all()
        return render_template('failures.html', failures=failures)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=8080)
