# 領養貓咪系統

## 專案結構
```
final/
├── static/                      # 靜態文件夾，包含CSS、圖片等
│   └── style.css                   # 設計
├── templates/                   # 頁面文件夾
│   ├── admin                    # 管理員
│   │   ├── cat_info.html           # 管理貓咪資料頁面
│   │   └── request_review.html     # 審核申請頁面
│   ├── user                     # 用戶
│   │   ├── dashboard.html          # 瀏覽頁面
│   │   └── request.html            # 申請領養頁面
│   ├── index.html               # 首頁
│   ├── login.html               # 登入頁面
│   ├── logout.html              # 登出頁面
│   └── signUp.html              # 用戶注冊頁面
├── app.py                       # 主程式，處理後端邏輯
└── README.md                    # 專案說明文件
```

---

## 專案描述
領養貓咪系統是一個面向愛貓人士的互動網站，用於瀏覽、申請領養貓咪，並幫助管理員高效處理領養申請。

該系統實現了用戶端和管理端功能，用戶可以查看貓咪詳情並提交領養申請，管理員則可以審核申請並管理貓咪資料。整個系統基於Flask框架，使用PostgreSQL作為數據存儲，並提供一個簡潔友好的界面。

---

## 技術架構
1. **前端技術**
   - **HTML**: 構建頁面結構。
   - **CSS**: 使用自定義樣式表和Bootstrap框架美化界面。
   - **JavaScript**: 提升用戶體驗，如表單驗證和動態加載內容。

2. **後端技術**
   - **Flask**: 作為後端框架，處理路由和業務邏輯。

3. **資料庫**
   - **PostgreSQL**: 儲存用戶信息、貓咪資料和領養申請記錄。

4. **開發與測試**
   - **Python**: 提供後端功能開發和數據處理。
   - **單元測試框架**: 確保代碼穩定性。

5. **部署**（????????????）
   - **XXXX**: 
   - **SSL加密**: 確保數據傳輸安全。

---

## 功能詳解

### 1. **用戶端功能**
   - 瀏覽待領養貓咪：
     - 查看貓咪列表，包括名字、年齡、性別、健康狀態等。
     - 點擊貓咪可進入詳情頁，查看更詳細的描述和圖片。
   - 領養申請：
     - 填寫申請表，提交領養需求。
     - 自定義領養日期，說明領養原因。

### 2. **管理端功能**
   - 貓咪管理：
     - 新增、修改、刪除貓咪資料。
     - 更新貓咪領養狀態（如“待領養”、“已領養”）。
   - 領養申請管理：
     - 查看所有申請，根據用戶信息進行審核。
     - 設定申請狀態（如“通過”或“拒絕”）。

### 3. **資料庫功能**
   - 貓咪表（Cats）： 存儲貓咪的基本信息
        - 名字
        - 年齡
        - 性別
        - 品種
        - 健康狀況(疫苗/絕育...)
        - 性格
   - 用戶表（Users）：存儲領養者的基本信息
        - 用戶名username
        - 密碼 password
        - 年齡
        - 性別
        - 聯絡方式
   - 領養申請表（Adoptions）：記錄每次申請的詳細信息
        - 用戶
        - 貓咪
        - 申請原因
        - 欲領養日期
        - 申請狀態
```
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    age INT,
    gender VARCHAR(10),
    contact VARCHAR(255)
);

CREATE TABLE cats (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    health_status VARCHAR(50),
    personality TEXT,
    adoption_status VARCHAR(20) DEFAULT 'available'
);

CREATE TABLE adoptions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    cat_id INT REFERENCES cats(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    planned_date DATE,
    status VARCHAR(20) DEFAULT 'pending'
);
```
---

## 安裝與運行

### 安裝依賴
1. 確保已安裝Python 3和PostgreSQL。
2. 安裝所需Python庫：
   ```bash
   pip install flask psycopg2
   ```

### 初始化資料庫
1. 創建PostgreSQL數據庫並導入初始化腳本（`init.sql`）。
2. 確保在`app.py`中更新正確的數據庫連接配置。

### 運行項目
1. 啟動Flask伺服器：
   ```bash
   python app.py
   ```
2. 在瀏覽器中打開`http://localhost:5000`訪問網站。

---

## 專案總結
- 領養貓咪系統實現了從用戶提交到管理端審核的完整流程。
- 整個系統結構清晰，基於Flask和PostgreSQL，具備良好的擴展性。
- 該專案結合實際需求，展現了強大的後端功能與友好的用戶界面，對社會公益有積極意義。

---

