from classes import *
import threading
from crawler_catwelfare import crawl_catwelfare
from crawler_petfinder import crawl_petfinder
from math import ceil, floor
import time
import requests

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1325838177231175801/YDoLRxKOUNZjakBz4Se4EZcsvNTzUPLKdOtk0wzCmEMqQCqLgb9rfokTtdaV3MDPRMhR'

# 首頁
@app.route('/')
def home():
    return render_template('index.html', logged_in=current_user.is_authenticated)

# 登入和註冊
@app.route('/login_signUp', methods=['GET', 'POST'])
def login_signUp():
    tab = request.args.get('tab', 'login')  # 默認顯示登入表單

    if tab == 'login' and request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password', 'danger')

    elif tab == 'signup' and request.method == 'POST':
        username = request.form['username']
        contact = request.form['contact']
        age = request.form['age']  
        gender = request.form['gender']  
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords are inconsistent', 'warning')
            return redirect(url_for('login_signUp', tab='signup'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('This username is already taken', 'warning')
        elif len(password) < 8:  # 簡單的密碼強度檢查
            flash('Password length must be at least 8 characters', 'warning')
        else:
            try:
                user = User(
                    username=username, 
                    contact=contact, 
                    age=int(age),  
                    gender= 1 if gender=='Male' else 0
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('Registration successful, please log in!', 'success')
                return redirect(url_for('login_signUp', tab='login'))
            except Exception as e:
                db.session.rollback()
                flash('There was a problem while registering, please try again!', 'danger')

    return render_template('login_signUp.html', tab=tab)

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))

# ---------------------------- 用戶路由   --------------------------
# 用戶：顯示所有貓咪資訊
@app.route('/user/dashboard', methods=['Get', 'POST'])
@login_required
def dashboard():
    per_page = 15
    page = request.args.get('page', 1, type=int)
    query = Cat.query
    global_query = GlobalCat.query

    if request.method == 'POST':
        name = request.form.get('cat_name')
        gender = request.form.get('cat_gender')
        age = request.form.get('cat_age')
        
        if name:
            query = query.filter(Cat.name.ilike(f'%{name}%'))
            global_query = global_query.filter(GlobalCat.name.ilike(f'%{name}%'))
        if gender:
            gender = 0 if gender=='Female' else 1
            query = query.filter(Cat.gender == gender)
            global_query = global_query.filter(GlobalCat.gender == gender)
        if age:
            age_range = [(range(-1,-1),-1), (range(0,2), -2), (range(2,4),-3), (range(4,8),-4)]
            query = query.filter(Cat.age == int(age))
            range_id = -1
        
            for i in age_range:
                if int(age) in i[0]:    
                    range_id = i[1]
                    break                        
            global_query = global_query.filter(GlobalCat.age == int(age) or GlobalCat.age == range_id)
            
    totalsize = query.count() + global_query.count()
    cats = query.offset((page-1) * per_page).limit(per_page).all()
    change_page = (1 + len(cats) // per_page) if len(cats) >= per_page else 1
    offset = len(cats) % per_page

    globalcats = []    
    if page >= change_page:
        print(page, per_page * (page - change_page - 1) + (per_page - offset) if page != change_page else 0)
        globalcats = global_query.offset(
            per_page * (page - change_page - 1) + (per_page - offset) if page != change_page else 0
        ).limit(max(per_page - len(cats), 0)).all()  # 確保 globalcats 的數量不會超過 per_page

    return render_template('user/dashboard.html', cats=cats, globalcats=globalcats, pageinfo=(page, ceil(totalsize/per_page)))

# 用於獲取貓咪詳細信息
@app.route('/api/cat/<int:cat_id>')
def get_localcat(cat_id):
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
            'img': cat.img#.decode('utf-8') if cat.img else None  # 將圖片轉為 Base64 字符串返回（若需要）
        },
        'user_name' : user.username,
        'user_contact': user.contact  # 包含用戶的聯繫方式
    })
    
@app.route('/api/globalcat/<int:cat_id>')
def get_globalcat(cat_id):
    # 查詢貓咪及其關聯用戶
    cat = GlobalCat.query.get_or_404(cat_id)
    
    # 返回 JSON 數據，包括貓咪信息和用戶聯繫方式
    return jsonify({
        'cat': {
            'id': cat.id,
            'name': cat.name,
            'age': cat.age,
            'gender': cat.gender,
            'health_status': cat.health_status,
            'personality': cat.personality,
            'img': cat.img#.decode('utf-8') if cat.img else None  # 將圖片轉為 Base64 字符串返回（若需要）
        },
        'link_contact': cat.linker,
        'src': cat.src
    })


# 用戶：領養申請
@app.route('/user/manage_request', methods=['GET', 'POST'])
@login_required
def manage_request():
    request_successful = False
    requests_query = Request.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        file = request.files.get('cat_image')
        if file:
            files = {'file': (file.filename, file.stream, file.mimetype)}
            response = requests.post(DISCORD_WEBHOOK_URL, files=files)
            
            if response.status_code != 200:
                return jsonify({"error": "無法上傳圖片到 Discord"}), 500
            
            discord_response = response.json()
            image_url = discord_response['attachments'][0]['url']
            file = image_url
        else:
            file = 'Unknown'
        
        new_request = Request(
                user_id = current_user.id,  
                cat_name = request.form.get('cat_name'),  
                cat_age = request.form.get('age'),  
                cat_gender = request.form.get('gender'),  
                cat_health_status = request.form.get('health_status'), 
                cat_personality = request.form.get('personality'),
                img = image_url,  
                reason = request.form.get('reason'), 
                status = 0
            )
        db.session.add(new_request)
        db.session.commit()
        request_successful = True
        # 重定向到当前页面，并附加成功提示参数
        return redirect(url_for('manage_request', request_successful=request_successful))  # 重新定向到當前頁面，避免重複提交表單
    return render_template('user/request.html', requests_query=requests_query, request_successful=request_successful)


@app.route('/api/requestCat/<int:request_id>', methods=['GET'])
def get_request_data(request_id):
    print(f"Received request_id: {request_id}")  
    try:
        # 查找指定 ID 的請求資料，若找不到則返回 404
        request_cat = Request.query.get_or_404(request_id)
        user = User.query.get(request_cat.user_id)  
        request_data = {
            "cat": {
                "name": request_cat.cat_name,
                "age": request_cat.cat_age,
                "gender": request_cat.cat_gender,
                "health_status": request_cat.cat_health_status,
                "personality": request_cat.cat_personality,
                "img": request_cat.img
            },
            "request": {
                "status": request_cat.status,
                "special_hint": request_cat.special_hint
            },
            'user_name': user.username,
            'user_contact': user.contact
        }
        return jsonify(request_data)
    except Exception as e:
        print(f"Error occurred: {e}")  
        return jsonify({"error": "Something went wrong."}), 500

# ---------------------------- 管理員路由  -------------------------------
# 管理員：貓咪資料頁面
@app.route('/admin/cat_info', methods=['GET', 'POST'])
@login_required
def admin_cat_info():
    per_page = 15
    page = request.args.get('page', 1, type=int)
    query = Cat.query
    global_query = GlobalCat.query

    if request.method == 'POST':
        name = request.form.get('cat_name')
        gender = request.form.get('cat_gender')
        age = request.form.get('cat_age')
        
        if name:
            query = query.filter(Cat.name.ilike(f'%{name}%'))
            global_query = global_query.filter(GlobalCat.name.ilike(f'%{name}%'))
        if gender:
            gender = 0 if gender=='Female' else 1
            query = query.filter(Cat.gender == gender)
            global_query = global_query.filter(GlobalCat.gender == gender)
        if age:
            age_range = [(range(-1,-1),-1), (range(0,2), -2), (range(2,4),-3), (range(4,8),-4)]
            query = query.filter(Cat.age == int(age))
            range_id = -1
        
            for i in age_range:
                if int(age) in i[0]:    
                    range_id = i[1]
                    break                        
            global_query = global_query.filter(GlobalCat.age == int(age) or GlobalCat.age == range_id)
            
    totalsize = query.count() + global_query.count()
    cats = query.offset((page-1) * per_page).limit(per_page).all()
    change_page = (1 + len(cats) // per_page) if len(cats) >= per_page else 1
    offset = len(cats) % per_page

    globalcats = []
    if page >= change_page:
        print(page, per_page * (page - change_page - 1) + (per_page - offset) if page != change_page else 0)
        globalcats = global_query.offset(
            per_page * (page - change_page - 1) + (per_page - offset) if page != change_page else 0
        ).limit(max(per_page - len(cats), 0)).all()  # 確保 globalcats 的數量不會超過 per_page

    return render_template('admin/cat_info.html', cats=cats, globalcats=globalcats, pageinfo=(page, ceil(totalsize/per_page)))

# 管理員：領養申請審核頁面
@app.route('/admin/request_review', methods=['GET', 'POST'])
@login_required
def admin_request_review():
    page = request.args.get('page', 1, type=int)  # 取得頁碼，預設是第1頁
    query = Request.query  # 初始化查詢

    if request.method == 'POST':
        # 取得表單提交的數據
        cat_name = request.form.get('cat_name')
        cat_gender = request.form.get('cat_gender')
        cat_age = request.form.get('cat_age')
        status = request.form.get('status')
        
        # 打印提交的數據進行調試
        print(f"cat_name: {cat_name}, cat_gender: {cat_gender}, cat_age: {cat_age}, status: {status}")
        
        # 根據表單數據建立查詢條件
        if cat_name:
            query = query.filter(Request.cat_name.ilike(f'%{cat_name}%'))  # 模糊查詢貓咪名字
        if cat_gender:
            # 映射性別，假設 Male = 1, Female = 0
            gender_mapping = {'Male': 1, 'Female': 0}
            if cat_gender in gender_mapping:
                query = query.filter(Request.cat_gender == gender_mapping[cat_gender])
        if cat_age:
            query = query.filter(Request.cat_age == int(cat_age))  # 查詢年齡
        if status:
            query = query.filter(Request.status == int(status))  # 查詢狀態

    # 執行分頁查詢
    requests = query.paginate(page=page, per_page=10)

    # 為每個請求加載對應的用戶信息
    for req in requests.items:
        req.user = User.query.get(req.user_id)  # 根據 user_id 查找對應的用戶

    return render_template('admin/request_review.html', requests=requests)

@app.route('/api/refetch', methods=['GET'])
def refetch():
    try:
        db.session.query(GlobalCat).delete()
        db.session.commit()
        threading.Thread(target=crawl_catwelfare(True)).start()
        time.sleep(1)
        threading.Thread(target=crawl_petfinder(False)).start()
        return jsonify({"message": "Refetch successful."})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Something went wrong."}), 500

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