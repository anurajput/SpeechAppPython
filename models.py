#
# script for various ORM models for project
#

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://speechapp:123@localhost/speechdb'
db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(90))
    email = db.Column(db.String(90))
    password = db.Column(db.String(90))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    @property
    def serialize(self):
        """ Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at
        }


class Paragraph(db.Model):

    __tablename__ = 'paragraph'

    id = db.Column(db.BigInteger, primary_key=True)
    paragraph = db.Column(db.String(90))
    user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, paragraph, user_id, created_at):
        self.id = id
        self.paragraph = paragraph
        self.user_id = user_id
        self.created_at = created_at

    @property
    def serialize(self):
        """Return object data in easily serialzeable format"""
        return {
            'id': self.id,
            'paragraph': self.paragraph,
            'user_id': self.user_id,
            'created_at': self.created_at
        }


class Study(db.Model):

    __tablename__ = 'study'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey('user.id'))
    text_id = db.Column(db.BigInteger)
    text = db.Column(db.String(90))
    paragraph = db.Column(db.String(90))
    created_at = db.Column(db.TIMESTAMP,
                           default=datetime.utcnow, nullable=False)

    def __init__(self, id, user_id, text_id, text, paragraph):
        self.id = id
        self.user_id = user_id
        self.text_id = text_id
        self.text = text
        self.paragraph = paragraph

    @property
    def serialize(self):
        """Return object data in easily serialzeable format"""
        return {
            'id': self.id,
            'text_id': self.text_id,
            'text': self.text,
            'user_id': self.user_id,
            'paragraph': self.paragraph,
            'created_at': self.created_at
        }


if __name__ == '__main__':
    try:
        db.create_all()
        print "===================== [db created] ====================="
    except Exception as exp:
        print "[Postgres Models] :: main() :: Got Exception: %s" % exp
        print "===================== [db not created] ================="
