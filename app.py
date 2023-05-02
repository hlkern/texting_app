from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Chat from {self.sender}>"



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return render_template('login.html', error=True)

        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html', error=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    return "You are logged in as " + current_user.username

@app.route('/chat', methods=['GET', 'POST'])
@login_required # yalnızca oturumu açık kullanıcılar sayfayı görüntüleyebilir
def chat():
    # sohbet mesajlarını veritabanından çekiyoruz
    chat_history = Chat.query.order_by(Chat.timestamp.asc())

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            # mesaj veritabanına kaydediliyor
            chat_message = Chat(sender=current_user.username, message=message)
            db.session.add(chat_message)
            db.session.commit()
    return render_template('chat.html', chat_history=chat_history)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    users = User.query.all()
    if request.method == 'POST':
        selected_user_id = request.form.get('user_id')
        selected_user = User.query.filter_by(id=selected_user_id).first()
        return redirect(url_for('chat', recipient=selected_user.username))
    return render_template('home.html', users=users)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

