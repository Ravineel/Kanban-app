from pyparsing import dblSlashComment
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model):
    __tablename__ = 'user'
    u_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=True)
    mail = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)

class Login(db.Model, UserMixin):
    __tablename__ = 'login'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    username = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def get_id(self):
           return (self.u_id)
    @property
    def password(sePlf):
        raise AttributeError("Not readable")
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
        
class List(db.Model):
    __tablename__ ='list'
    l_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.u_id'))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)