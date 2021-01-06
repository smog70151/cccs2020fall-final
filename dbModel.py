from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
from config import POSTGRES

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:xxxxx@localhost/db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_POOL_SIZE'] = 0
app.config['SQLALCHEMY_MAX_OVERFLOW'] = -1

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class UserAccounts(db.Model):
    __tablename__ = 'UserAccounts'

    Id = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(64), unique=True)
    Password = db.Column(db.String(64))
    MugShot = db.Column(db.String(64))
    CreateDate = db.Column(db.DateTime)
    ModifiedDate = db.Column(db.DateTime)
    Role = db.Column(db.Boolean)

    def __init__(self,
                 user_name,
                 password,
                 mugshot,
                 role,
                 create_date=datetime.now(),
                 modified_date=datetime.now()):
        self.UserName = user_name
        self.Password = self.psw_to_md5(password)
        self.MugShot = mugshot
        self.CreateDate = create_date
        self.ModifiedDate = modified_date
        self.Role = role

    @staticmethod
    def psw_to_md5(str_psw):
        import hashlib
        if not str_psw:
            return None
        else:
            m = hashlib.md5(str_psw.encode(encoding='utf-8'))
            return m.hexdigest()


class Message(db.Model):
    __tablename__ = 'Message'

    Id = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(64))
    Messages = db.Column(db.Text)
    CreateDate = db.Column(db.DateTime)
    RoomId = db.Column(db.String(64))

    def __init__(self,
                 user_name,
                 messages,
                 create_date,
                 room_id):
        self.UserName = user_name
        self.Messages = messages
        self.CreateDate = create_date
        self.RoomId = room_id

class Room(db.Model):
    __tablename__ = 'Room'

    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(64))
    URL = db.Column(db.String(64))
    UserID = db.Column(db.String(64))

    def __init__(self,
                 title,
                 url,
                 user_id):
        self.Title = title
        self.URL = url
        self.UserID = user_id

    @staticmethod
    def md5(str_psw):
        import hashlib
        if not str_psw:
            return None
        else:
            m = hashlib.md5(str_psw.encode(encoding='utf-8'))
            return m.hexdigest()

if __name__ == '__main__':
    manager.run()
