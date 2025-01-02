-- 全球貓咪表 (global_cats)
CREATE TABLE global_cats (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    name VARCHAR(100) NOT NULL,           -- 名字
    age VARCHAR(30),                      -- 年齡
    gender VARCHAR(10),                   -- 性別
    health_status VARCHAR(255),           -- 健康狀況（如疫苗、絕育等）
    personality TEXT,                     -- 性格描述
    img VARCHAR(255),                     -- 圖片網址
    linker VARCHAR(255),                   -- 連結原始網址
    src VARCHAR(50)                       -- 來源名稱
);

-- 本地貓咪表 (local_cats)
CREATE TABLE local_cats (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,           -- 名字
    age VARCHAR(30),                      -- 年齡
    gender VARCHAR(10),                   -- 性別
    health_status VARCHAR(255),           -- 健康狀況（如疫苗、絕育等）
    personality TEXT,                     -- 性格描述
    img VARCHAR(255)                      -- 圖片網址
);

-- 用戶表 (users)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                -- 唯一標識
    username VARCHAR(150) NOT NULL UNIQUE, -- 用戶名
    password_hash TEXT NOT NULL,          -- 密碼（經過哈希處理）
    age INT,                              -- 年齡
    gender VARCHAR(10),                   -- 性別   
    contact VARCHAR(255)                  -- 聯絡方式
    is_admin BOOLEAN DEFAULT FALSE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 記錄創建時間
);

-- 領養表 (Adoption)
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
    status SMALLINT DEFAULT 0,             -- 申請狀態：-1審核失敗，0等待審核，1等待領養，2領養申請中，3領養成功
    special_hint VARCHAR(255),             -- 特殊提示：未通過時使用這裡告知未通過原因
    adopter_id INT REFERENCES users(id),  -- 領養者
    adopter_date DATE DEFAULT CURRENT_DATE-- 領養日期
);

-- 創建管理員賬號(密碼：meowtopia)
INSERT INTO users (username, password_hash, is_admin) 
VALUES ('admin', 'scrypt:32768:8:1$nmV9LvPJFOhQrYdD$e290620bc07bde8204a81431cf30804349ff7c283e89ae2784a0ab7aaa004742c8ad222b79da0dc314807307c78f48aa0c2c47f45142646674f1d5124a973ce2', TRUE);