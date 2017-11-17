#coding:utf-8
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

class Permission:
    VISITOR = 0x55      # 旅游者可以访问权限值在0x55以下的内容
    ROUTER = 0xAA       # 旅行社可以访问权限值在0xAA以下的内容
    SCENICER = 0xFE     # 景区管理员可以访问权限值在0xFE以下的内容
    ADMINISTER = 0xFF   # 网站管理者可以访问权限值在0xFF以下的内容（全部内容）

class Scenic(db.Model):
    __tablename__ = 'scenic'
    item = db.Column(db.String(64), unique=True,primary_key=True)
    intro = db.Column(db.String(64))
    opentime = db.Column(db.String(64))
    position = db.Column(db.String(64))
    price = db.Column(db.Integer)
    evaluate = db.Column(db.Float, default=0)  #游客为景点打分
    complain = db.Column(db.Integer, default=0)  #游客投诉量
    visit_num = db.Column(db.Integer, default=0) #累计游客数
    order_data = db.Column(db.String(1024), default=' ')

class Route(db.Model):
    __tablename__ = 'route'
    item = db.Column(db.String(64), unique=True,primary_key=True, default=' ')
    intro = db.Column(db.String(64), default=' ')
    gotime = db.Column(db.String(64), default=' ')
    backtime = db.Column(db.String(64), default=' ')
    scenic = db.Column(db.String(1024), default=' ')
    upper_num = db.Column(db.Integer, default=0)
    lower_num = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(64), default=' ')
    current_num = db.Column(db.Integer, default=0)
    order_data = db.Column(db.String(1024), default=' ')
    eat = db.Column(db.String(1024), default=' ')
    sleep = db.Column(db.String(1024), default=' ')
    company = db.Column(db.String(64), default=' ')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'VISITOR': (Permission.VISITOR , True),
            'ROUTER': (Permission.ROUTER , False),
            'SCENICER': (Permission.SCENICER , False),
            'Administrator': (Permission.ADMINISTER, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True, default=' ')
    username = db.Column(db.String(64), unique=True, index=True, default=' ')
    radio = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64), default=' ')
    location = db.Column(db.String(64), default=' ')
    about_me = db.Column(db.Text(), default=' ')
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(64), default=' ')
    scenic = db.Column(db.String(1024), default=' ')
    route = db.Column(db.String(1024), default=' ')
    company = db.Column(db.String(64),default=' ')



    @staticmethod
    def insert_users():
        users = {
            'admin@trip.com': ('测试-开发者帐号','3',3,'pbkdf2:sha1:1000$2ggZDUpS$3823dad5c2c796cd49621c4de89d0a94773d4312',1,'开发者','北京','测试帐号','010-66666666',' '),
            'router@trip.com': ('测试-旅行社管理员','2',4,'pbkdf2:sha1:1000$V8jhHTfG$4f7b3732543d03aaf9a56de971ba3bee210ee9f0',1,'线路管理','北京', '测试帐号','010-66666666','xxx旅行社'),
            'scenicer@trip.com': ('测试-景区管理员','1',2,'pbkdf2:sha1:1000$Ts6bLY7Z$04989e065e370f54c59ee3514edae58de7dd6edf',1,'景区管理','北京', '测试帐号','010-66666666',' '),
            'visitor@trip.com': ('测试-游客','3',1,'pbkdf2:sha1:1000$iYL4sSBt$815974daae1f72137d2064d03ed96da07c546927',1,'普通游客','北京','测试帐号','010-66666666',' ')
        }
        for u in users:
            user = User.query.filter_by(email=u).first()
            if user is None:
                user = User(email=u)
            user.username = users[u][0]
            user.radio = users[u][1]
            user.role_id = users[u][2]
            user.password_hash = users[u][3]
            user.confirmed = users[u][4]
            user.name = users[u][5]
            user.location = users[u][6]
            user.about_me = users[u][7]
            user.phone = users[u][8]
            user.company = users[u][9]
            db.session.add(user)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions #按位与实现比较权限大小，并返回权限高低

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_SCENICER(self):
        return self.can(Permission.SCENICER)

    def is_ROUTER(self):
        return self.can(Permission.ROUTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):#匿名用户
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_SCENICER(self):
        return False

    def is_ROUTER(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))