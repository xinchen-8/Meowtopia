from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField    # 創建表單欄位
from wtforms.validators import DataRequired     # 用於表單欄位來檢查是否填寫了必填字段
from datetime import datetime

app = Flask(__name__)
# 配置數據庫連接
app.config['SECRET_KEY'] = 'meowtopia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:87518875@localhost/Meowtopia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 用戶類別
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)    # 用戶名，不可重複
    password_hash = db.Column(db.String(128))                           # 加密後的密碼
    age = db.Column(db.Integer)  
    gender = db.Column(db.String(10))
    contact = db.Column(db.String(255))
    cats = db.relationship('Cat', backref='owner', lazy=True)  # 與 Cat 的反向關聯
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)        # 創建時間
    is_admin = db.Column(db.Boolean, default=False)  # 預設為 False（普通用戶）
    #adoptions = db.relationship('Adoption', backref='user', lazy=True)  # 申請領養資料

    # 必须实现 Flask-Login 的方法
    def is_authenticated(self):
        # 此方法用来返回是否已认证
        return True  # 或者根据你的需求添加额外的逻辑

    def is_active(self):
        # 你可以根据需要修改这个方法，默认返回 True 表示账户活跃
        return True

    def get_id(self):
        # 返回用户的唯一 ID
        return str(self.id)

    # 密碼設置
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 密碼驗證（登入用途）
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 貓咪類別
class Cat(db.Model):
    __tablename__ = 'local_cats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用戶 ID，外鍵
    name = db.Column(db.String(80), nullable=False)                     # 貓咪名字
    age = db.Column(db.String(15))                                      # 年齡
    gender = db.Column(db.String(10))                                   # 性別
    health_status = db.Column(db.Text)                                  # 健康狀況
    personality = db.Column(db.Text)                                    # 性格特點
    img =  db.Column(db.LargeBinary)                                    # 存儲照片的二進制數據
    #adoption_status = db.Column(db.String(20), default='available')     # 領養狀態
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)        # 創建時間
    #adoptions = db.relationship('Adoption', backref='cat', lazy=True)   # 與領養申請的關聯

    # 定義與用戶表的關聯
    user = db.relationship('User', backref=db.backref('local_cats', lazy=True))

class GlobalCat(db.Model):
    __tablename__ = 'global_cats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)                     # 貓咪名字
    age = db.Column(db.String(15))                                         # 年齡
    gender = db.Column(db.String(10))                                   # 性別
    health_status = db.Column(db.Text)                                  # 健康狀況
    personality = db.Column(db.Text)                                    # 性格特點
    img = db.Column(db.String(255))                                     # 圖片網址
    linker = db.Column(db.String(255))                                  # 網站來源
    src = db.Column(db.String(50))                                      # 網站名稱
    #adoption_status = db.Column(db.String(20), default='available')     # 領養狀態
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)        # 創建時間
    #adoptions = db.relationship('Adoption', backref='cat', lazy=True)   # 與領養申請的關聯


# # 領養申請類別
# class Adoption(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 申請人ID
#     cat_name = db.Column(db.String(100), nullable=False)  # 貓咪名字
#     cat_age = db.Column(db.Integer)  # 貓咪年齡
#     cat_gender = db.Column(db.String(10))  # 貓咪性別
#     cat_health_status = db.Column(db.String(255))  # 貓咪健康狀況
#     cat_personality = db.Column(db.Text)  # 貓咪性格

#     # 申請信息
#     reason = db.Column(db.Text, nullable=False)  # 申請原因
#     request_date = db.Column(db.Date, default=datetime.utcnow)  # 申請日期
#     status = db.Column(db.SmallInteger, default=0)  # 申請狀態：-1未通過，0等待審核，1通過等待領養，2通過且成功被領養
    
#     # 其他
#     hint = db.Column(db.String(255))  # 特殊提示
#     adopter_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 領養者 (外鍵, 連接到用戶表)
#     adopter_date = db.Column(db.Date, default=datetime.utcnow)  # 領養日期

#     # 關聯 User 表（申請者）和 Cat 表（貓咪）
#     user = db.relationship('User', backref='adoption_requests', lazy=True)
#     cat = db.relationship('Cat', backref='adoption_requests', lazy=True)
#     adopter = db.relationship('User', foreign_keys=[adopter_id], backref='adopted_requests', lazy=True)


