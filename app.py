from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///urls.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
app.config['REMOVAL_INTERVAL'] = int(os.environ.get('REMOVAL_INTERVAL', 30)) # days

db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(10), unique=True, nullable=False)
    long_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/<path:path>')
def redirect_to_url(path):
    url = Url.query.filter_by(short_url=path).first()
    if url:
        return redirect(url.long_url)
    else:
        return "Short URL doesn't exist."

@app.route('/shorten')
def shorten():
    url = request.args.get('url')
    if not url:
        return 'Please provide a URL to shorten.', 400

    short_url = generate_short_url()

    new_url = Url(short_url=short_url, long_url=url)
    db.session.add(new_url)
    db.session.commit()

    #return f'Short URL for {url}: {request.host_url}{short_url}'
    return request.host_url+short_url

def generate_short_url():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    short_url = ''.join(random.choice(chars) for _ in range(6))

    while Url.query.filter_by(short_url=short_url).first():
        short_url = ''.join(random.choice(chars) for _ in range(6))

    return short_url

def init_db():
    db.create_all()

def cleanup():
    now = datetime.utcnow()
    urls_to_delete = Url.query.filter(Url.created_at < now - timedelta(days=app.config['REMOVAL_INTERVAL'])).all()
    for url in urls_to_delete:
        db.session.delete(url)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup, trigger="interval", days=app.config['REMOVAL_INTERVAL'])
    scheduler.start()
    app.run(debug=True, host='0.0.0.0', port=8080)
