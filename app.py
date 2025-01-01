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
    per_page = 15  # 每頁顯示 15 個貓咪（3列 * 5行）

    page = request.args.get('page', 1, type=int)  # 取得當前頁數，預設為第 1 頁
    cats = Cat.query.paginate(page=page, per_page=per_page, error_out=False)  # 分頁查詢貓咪資料

    return render_template('user/dashboard.html', cats=cats)

# 用於獲取貓咪詳細信息
@app.route('/api/cat/<int:cat_id>')
def get_cat(cat_id):
    # 查詢貓咪及其關聯用戶
    cat = Cat.query.get_or_404(cat_id)
    user = User.query.get_or_404(cat.user_id)  # 通過關聯屬性獲取用戶信息
    
    # 返回 JSON 數據，包括貓咪信息和用戶聯繫方式
    return jsonify({
        'cat': {
            'id': cat.id,
            'name': cat.name,
            'age': cat.age,
            'gender': cat.gender,
            'health_status': cat.health_status,
            'personality': cat.personality,
            'img': cat.img.decode('utf-8') if cat.img else None  # 將圖片轉為 Base64 字符串返回（若需要）
        },
        'user_contact': user.contact  # 包含用戶的聯繫方式
    })

# 用戶：領養申請
@app.route('/user/manage_request')
@login_required
def manage_request():
    return render_template('user/request.html')

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