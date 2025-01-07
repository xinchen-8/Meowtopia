from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms import StringField, SubmitField, DateField, SelectField    # 創建表單欄位
from wtforms.validators import DataRequired     # 用於表單欄位來檢查是否填寫了必填字段
from datetime import datetime
import os
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 文件
app = Flask(__name__)
# 配置數據庫連接
app.config['SECRET_KEY'] = 'Jin_xin0816' # meowtopia
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 初始化 Migrate
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 用戶類別
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)    # 用戶名，不可重複
    password_hash = db.Column(db.String(128))                           # 加密後的密碼
    age = db.Column(db.Integer)  
    gender = db.Column(db.Integer)
    contact = db.Column(db.String(300))
    cats = db.relationship('Cat', backref='owner', lazy=True)  # 與 Cat 的反向關聯
    is_admin = db.Column(db.Boolean, default=False)  # 預設為 False（普通用戶）

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
    name = db.Column(db.String(100), nullable=False)                     # 貓咪名字
    age = db.Column(db.Integer)                                      # 年齡
    gender = db.Column(db.Integer)                                   # 性別
    health_status = db.Column(db.String(300))                                  # 健康狀況
    personality = db.Column(db.String(300))                                    # 性格特點
    img =  db.Column(db.String(300))                                    # 存儲照片的二進制數據

    # 定義與用戶表的關聯
    user = db.relationship('User', backref=db.backref('local_cats', lazy=True))

class GlobalCat(db.Model):
    __tablename__ = 'global_cats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)                     # 貓咪名字
    age = db.Column(db.Integer)                                         # 年齡
    gender = db.Column(db.Integer)                                   # 性別
    health_status = db.Column(db.String(300))                                  # 健康狀況
    personality = db.Column(db.String(300))                                    # 性格特點
    img = db.Column(db.String(300))                                     # 圖片網址
    linker = db.Column(db.String(300))                                  # 網站來源
    src = db.Column(db.String(20))                                      # 網站名稱

# # 領養申請類別
class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)  # 唯一標識
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # 申請用戶ID
    cat_name = db.Column(db.String(100), nullable=False)  # 貓咪名字
    cat_age = db.Column(db.Integer)  # 貓咪年齡
    cat_gender = db.Column(db.Integer)  # 貓咪性別
    cat_health_status = db.Column(db.String(300))  # 貓咪健康狀況
    cat_personality = db.Column(db.String(300))  # 貓咪性格
    img = db.Column(db.String(300))  # 圖片網址
    reason = db.Column(db.Text, nullable=False)  # 申請原因
    status = db.Column(db.SmallInteger, default=0)  # 申請狀態：-1審核失敗，0等待審核，1等待領養，2領養申請中，3領養成功
    special_hint = db.Column(db.String(255))  # 特殊提示：未通過時使用這裡告知未通過原因
    adopter_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 領養者

    def get_status_class(self):
        status_classes = {
            -1: "failed",
            0: "waiting",
            1: "pending",
            2: "processing",
            3: "success"
        }
        return status_classes.get(self.status, "unknown")
