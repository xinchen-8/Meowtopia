# 喵托邦

## 專案結構
```
final/
├── static/                      # 靜態文件夾，包含CSS、圖片等
│   ├── card_cat.css             
│   └── style.css
├── templates/                   # 頁面文件夾
│   ├── admin                    # 管理員專屬頁面
│   │   ├── cat_info.html           # 管理貓咪資料頁面
│   │   └── request_review.html     # 審核用戶新增領養申請頁面
│   ├── request.html             # 新增並填寫想要被領養貓咪的資訊
│   ├── dashboard.html           # 瀏覽頁面
│   ├── index.html               # 首頁
│   ├── login_signUp.html        # 用戶登入/注冊頁面 
│   └── logout.html              # 登出頁面
├── app.py                       # 主程式，處理後端邏輯
└── README.md                    # 專案說明文件
```

---

## 專案描述
喵托邦是一個專為愛貓人士打造的互動網站，通過爬蟲整合多家流浪貓收容所的領養資訊，並允許用戶提交新增貓咪領養資訊申請，管理員對申請進行審核後可將信息發布至網站。

系統包括用戶端和管理端功能：
- 用戶可瀏覽貓咪資訊、提交新增領養申請。
- 管理員可管理貓咪資訊、審核用戶申請。
整個系統基於Flask框架，數據存儲採用PostgreSQL，提供簡潔友好的界面，實現高效運作。
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

5. **部署**
   - **XXXX**: 
   - **SSL加密**: 確保數據傳輸安全。

---

## 功能詳解

### 1. 賬號登入登出
   - 用戶可註冊、登入及安全退出

### 2. 用戶端功能
   - 可以查看所有貓咪資訊
   - 新增領養資訊：
     - 填寫並上傳貓咪資料（見貓咪table）
     - 檢查貓咪資料上傳狀態（通過/駁回）
         - **通過**：綠色框框，若其他用戶要申請領養，會顯示
         - **駁回**：顯示駁回原因，可以讓用戶修改錯誤后再上傳

### 3. 管理端功能
   - 管理貓咪領養資訊
      - 可手動重新爬蟲獲取最新的流浪貓收容所的領養資訊
      - 可刪除不適合的領養資訊
   - 審核新增領養咨詢：
     - **檢查賬號是否為管理員**
         - 若是**管理員**：直接新增到資料庫
         - 否則：需要管理員審核
     - 查看所有申請，根據用戶上傳内容進行審核
     - 設定申請狀態（如“通過”或“拒絕”）
     - 拒絕理由（必填）

### 4. 資料庫功能
   - 創建管理員賬號(密碼：meowtopia)
   ```
   INSERT INTO users (username, password_hash, is_admin) 
VALUES ('admin', 'scrypt:32768:8:1$nmV9LvPJFOhQrYdD$e290620bc07bde8204a81431cf30804349ff7c283e89ae2784a0ab7aaa004742c8ad222b79da0dc314807307c78f48aa0c2c47f45142646674f1d5124a973ce2', TRUE);
   ```
   - 全球貓咪表（global cats）： 存儲爬蟲獲取的貓咪基本信息
        - id
        - 名字
        - 年齡
        - 性別
        - 健康狀況(疫苗/絕育...)
        - 性格
   - 本地貓咪表（local cats）:存儲管理員的審核通過的用戶所新增的領養貓資訊
         - id
         - 上傳用戶id
         - 名字
         - 年齡
         - 性別
         - 健康狀況(疫苗/絕育...)
         - 性格
   - 用戶表（users）：存儲領養者的基本信息
        - id
        - 用戶名username
        - 密碼 password (經過哈希處理)
        - 年齡
        - 性別
        - 聯絡方式
        - 創戶時間
   - 申請表（request）：記錄每次申請的詳細信息
        - id
        - 申請用戶ID
        - 貓咪資料（**貓咪表需要的**）
        - 申請原因
        - 申請日期
        - 申請狀態：-1未通過，0等待審核，1通過等待領養，2通過且成功被領養
```
-- 全球貓咪表 (global_cats)
CREATE TABLE global_cats (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    name VARCHAR(100) NOT NULL,           -- 名字
    age INT,                              -- 年齡
    gender VARCHAR(10),                   -- 性別
    health_status VARCHAR(255),           -- 健康狀況（如疫苗、絕育等）
    personality TEXT                      -- 性格描述
);

-- 用戶表 (users)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    username VARCHAR(150) NOT NULL UNIQUE, -- 用戶名
    password_hash TEXT NOT NULL,          -- 密碼（經過哈希處理）
    age INT,                              -- 年齡
    gender VARCHAR(10),                   -- 性別
    contact VARCHAR(255),                 -- 聯絡方式
    is_admin BOOLEAN DEFAULT FALSE        -- 檢查是不是admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 記錄創建時間
);

-- 本地貓咪表 (local_cats)
CREATE TABLE local_cats (
    id SERIAL PRIMARY KEY,                 -- 唯一標識
    user_id INT NOT NULL,                   -- 用戶 ID，外鍵參照 users 表
    name VARCHAR(100) NOT NULL,             -- 貓咪名字
    age INT,                                -- 貓咪年齡
    gender VARCHAR(10),                     -- 貓咪性別
    health_status VARCHAR(255),             -- 貓咪健康狀況（如疫苗、絕育等）
    personality TEXT,                       -- 貓咪性格描述
    img BYTEA,                              -- 貓咪圖片，使用 BYTEA 類型來存儲二進制數據
    FOREIGN KEY (user_id) REFERENCES users(id)  -- 外鍵，關聯到 users 表
);

-- 申請表 (requests)
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    user_id INT REFERENCES users(id) ON DELETE CASCADE, -- 申請用戶ID
    cat_name VARCHAR(100) NOT NULL,       -- 貓咪名字
    cat_age INT,                          -- 貓咪年齡
    cat_gender VARCHAR(10),               -- 貓咪性別
    cat_health_status VARCHAR(255),       -- 貓咪健康狀況
    cat_personality TEXT,                 -- 貓咪性格
    reason TEXT NOT NULL,                 -- 申請原因
    request_date DATE DEFAULT CURRENT_DATE, -- 申請日期
    status SMALLINT DEFAULT 0             -- 申請狀態：-1未通過，0等待審核，1通過等待領養，2通過且成功被領養
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
- 喵托邦實現了從用戶提交到管理端審核的完整流程。(待修)
- 整個系統結構清晰，基於Flask和PostgreSQL，具備良好的擴展性。
- 該專案結合實際需求，展現了強大的後端功能與友好的用戶界面，對社會公益有積極意義。

---

