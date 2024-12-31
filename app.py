from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField    # 創建表單欄位
from wtforms.validators import DataRequired     # 用於表單欄位來檢查是否填寫了必填字段
from datetime import datetime

app = Flask(__name__)
# 配置數據庫連接
app.config['SECRET_KEY'] = 'Jin_xin0816'
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:Jin_xin0816@localhost/my_hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 用戶類別
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)    # 用戶名，不可重複
    password_hash = db.Column(db.String(128))                           # 加密後的密碼
    age = db.Column(db.Integer)  
    gender = db.Column(db.String(10))  
    contact = db.Column(db.String(100))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)        # 創建時間
    adoptions = db.relationship('Adoption', backref='user', lazy=True)  # 申請領養資料

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)                     # 貓咪名字
    age = db.Column(db.Integer)                                         # 年齡
    gender = db.Column(db.String(10))                                   # 性別
    health_status = db.Column(db.Text)                                  # 健康狀況
    personality = db.Column(db.Text)                                    # 性格特點
    adoption_status = db.Column(db.String(20), default='available')     # 領養狀態
    created_at = db.Column(db.DateTime, default=datetime.utcnow)        # 創建時間
    adoptions = db.relationship('Adoption', backref='cat', lazy=True)   # 與領養申請的關聯

# 領養申請類別
class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 申請人ID
    cat_id = db.Column(db.Integer, db.ForeignKey('cats.id'), nullable=False)    # 貓咪ID
    reason = db.Column(db.Text)                                                 # 申請原因
    planned_date = db.Column(db.Date)                                           # 預計領養日期
    status = db.Column(db.String(20), default='pending')                        # 申請狀態
    created_at = db.Column(db.DateTime, default=datetime.utcnow)                # 創建時間



# 首頁
@app.route('/')
def home():
    return render_template('index.html')

# 登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

# 註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            age=request.form['age'],
            gender=request.form['gender'],
            contact=request.form['contact']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ---------------------------- 用戶路由   --------------------------
# 用戶：顯示所有貓咪資訊
@app.route('/user/dashboard')
@login_required
def dashboard():
    user_adoptions = current_user.adoptions  # 獲取當前用戶的所有領養申請
    return render_template('user/dashboard.html', adoptions=user_adoptions)


# 用戶：領養申請
@app.route('/user/request/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def adoption_request(cat_id):
    if request.method == 'POST':
        adoption = Adoption(
            user_id=current_user.id,
            cat_id=cat_id,
            reason=request.form['reason'],
            planned_date=request.form['planned_date']
        )
        db.session.add(adoption)
        db.session.commit()
        return redirect(url_for('dashboard'))
    cat = Cat.query.get_or_404(cat_id)
    return render_template('user/request.html', cat=cat)

# ---------------------------- 管理員路由  -------------------------------
# 管理員：貓咪資料頁面
@app.route('/admin/cat_info', methods=['GET', 'POST'])
@login_required
def admin_cat_info():
    if request.method == 'POST':
        cat = Cat(
            name=request.form['name'],
            age=request.form['age'],
            gender=request.form['gender'],
            health_status=request.form['health_status'],
            personality=request.form['personality']
        )
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('admin_cat_info'))
    cats = Cat.query.all()
    return render_template('admin/cat_info.html', cats=cats)

# 管理員：領養申請審核頁面
@app.route('/admin/request_review')
@login_required
def admin_request_review():
    adoptions = Adoption.query.filter_by(status='pending').all()
    return render_template('admin/request_review.html', adoptions=adoptions)

# 管理員：更新領養申請狀態
@app.route('/admin/request_review/<int:adoption_id>', methods=['POST'])
@login_required
def update_adoption_status(adoption_id):
    adoption = Adoption.query.get_or_404(adoption_id)
    adoption.status = request.form['status']
    if adoption.status == 'approved':
        adoption.cat.adoption_status = 'adopted'
    db.session.commit()
    return redirect(url_for('admin_request_review'))

if __name__ == '__main__':
    app.run(debug=True)