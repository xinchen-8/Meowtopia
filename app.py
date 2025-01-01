from classes import *

# 首頁
@app.route('/')
def home():
    return render_template('index.html', logged_in=current_user.is_authenticated)

# 登入和註冊
@app.route('/login_signUp', methods=['GET', 'POST'])
def login_signUp():
    tab = request.args.get('tab', 'login')  # 默認顯示登入表單

    if tab == 'login' and request.method == 'POST':
        # 登入邏輯
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('無效的用戶名或密碼', 'danger')

    elif tab == 'signup' and request.method == 'POST':
        # 註冊邏輯
        username = request.form['username']
        contact = request.form['contact']
        age = request.form['age']  
        gender = request.form['gender']  
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('密碼不一致', 'warning')
            return redirect(url_for('login_signUp', tab='signup'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('該用戶名已被使用', 'warning')
        elif len(password) < 8:  # 簡單的密碼強度檢查
            flash('密碼長度必須至少為 8 位', 'warning')
        else:
            try:
                user = User(
                    username=username, 
                    contact=contact, 
                    age=age,  
                    gender=gender
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('註冊成功，請登入！', 'success')
                return redirect(url_for('login_signUp', tab='login'))
            except Exception as e:
                db.session.rollback()
                flash('註冊時出現問題，請重試', 'danger')

    return render_template('login_signUp.html', tab=tab)

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # 清空 session
    return redirect(url_for('home'))

# ---------------------------- 用戶路由   --------------------------
# 用戶：顯示所有貓咪資訊
@app.route('/user/dashboard')
@login_required
def dashboard():
    user_adoptions = current_user.adoptions  # 獲取當前用戶的所有領養申請
    return render_template('user/dashboard.html', adoptions=user_adoptions)


# # 用戶：領養申請
# @app.route('/user/request/<int:cat_id>', methods=['GET', 'POST'])
# @login_required
# def adoption_request(cat_id):
#     if request.method == 'POST':
#         adoption = Adoption(
#             user_id=current_user.id,
#             cat_id=cat_id,
#             reason=request.form['reason'],
#             planned_date=request.form['planned_date']
#         )
#         db.session.add(adoption)
#         db.session.commit()
#         return redirect(url_for('dashboard'))
#     cat = Cat.query.get_or_404(cat_id)
#     return render_template('user/request.html', cat=cat)

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
# @app.route('/admin/request_review')
# @login_required
# def admin_request_review():
#     adoptions = Adoption.query.filter_by(status='pending').all()
#     return render_template('admin/request_review.html', adoptions=adoptions)

# 管理員：更新領養申請狀態
# @app.route('/admin/request_review/<int:adoption_id>', methods=['POST'])
# @login_required
# def update_adoption_status(adoption_id):
#     adoption = Adoption.query.get_or_404(adoption_id)
#     adoption.status = request.form['status']
#     if adoption.status == 'approved':
#         adoption.cat.adoption_status = 'adopted'
#     db.session.commit()
#     return redirect(url_for('admin_request_review'))

if __name__ == '__main__':
    app.run(debug=True)