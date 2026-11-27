-- ==========================================
-- 1. 共用功能：角色與使用者資料表
-- ==========================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO roles (name)
VALUES ('Admin'), ('Teacher'), ('User')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id) DEFAULT 3,
    status VARCHAR(20) NOT NULL DEFAULT 'approved', -- 帳號註冊後立即啟用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 舊資料庫若曾有待審核帳號，一併啟用
UPDATE users SET status = 'approved' WHERE status IN ('pending', 'rejected');

-- 預設測試帳號（密碼皆為 123456，且預設為已通過審核，方便三人開工測試）
INSERT INTO users (username, email, password, role_id, status)
VALUES 
    ('admin', 'admin@ibs.ncnu.edu.tw', '123456', 1, 'approved'),
    ('teacher1', 'teacher1@ibs.ncnu.edu.tw', '123456', 2, 'approved'),
    ('student1', 'student1@ibs.ncnu.edu.tw', '123456', 3, 'approved')
ON CONFLICT (username) DO NOTHING;

-- ==========================================
-- 2. 模組一（空間查詢）與跨模組共用：教室空間表
-- ==========================================
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    room_code VARCHAR(30) UNIQUE NOT NULL,       -- 例如：管201、管305
    name VARCHAR(100) NOT NULL,                  -- 例如：個案研討室、電腦教室
    floor VARCHAR(20),                           -- 例如：2F、3F
    capacity INTEGER DEFAULT 0,                  -- 容納人數
    equipment TEXT,                              -- 基本設備說明（單槍、白板等）
    description TEXT,                            -- 教室詳細介紹
    panorama_url TEXT,                           -- 360 全景照片路徑或網址 (Pannellum)
    floor_plan_image TEXT,                       -- 對應樓層平面圖路徑
    map_x NUMERIC(5, 2),                         -- 教室在平面圖上的 X 座標百分比 (0~100)
    map_y NUMERIC(5, 2),                         -- 教室在平面圖上的 Y 座標百分比 (0~100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 預設管院測試教室資料
INSERT INTO rooms (room_code, name, floor, capacity, equipment, description, map_x, map_y)
VALUES 
    ('管201', '管院大型階梯教室', '2F', 120, '雙投影機、無線麥克風、講桌電腦', '適合大型演講與大班授課', 35.5, 42.0),
    ('管302', '哈佛個案研討室', '3F', 60, '環形白板、電子講桌、視訊設備', 'U型階梯座位，適合分組討論', 62.0, 28.5),
    ('管405', '資訊管理電腦教室', '4F', 55, '55台桌上型電腦、廣播教學系統', '配備完整資料分析與開發軟體', 48.0, 70.0)
ON CONFLICT (room_code) DO NOTHING;

-- ==========================================
-- 3. 模組二（空間/物品預約借用）：物品與借用紀錄表
-- ==========================================
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,            -- 例如：教室鑰匙、投影筆、筆電、延長線
    total_quantity INTEGER NOT NULL DEFAULT 1
);

INSERT INTO items (name, total_quantity)
VALUES 
    ('教室鑰匙', 10),
    ('無線投影筆', 5),
    ('借用筆記型電腦', 3),
    ('HDMI轉接頭', 8)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    booking_date DATE NOT NULL,                  -- 借用日期
    start_time TIME NOT NULL,                    -- 開始時間
    end_time TIME NOT NULL,                      -- 結束時間
    purpose TEXT,                                -- 借用事由
    status VARCHAR(20) NOT NULL DEFAULT 'pending',        -- pending(待審核), approved(通過), rejected(退件)
    admin_comment TEXT,                                   -- 管理員審核意見
    handover_status VARCHAR(20) NOT NULL DEFAULT 'none',  -- none(未領用), borrowed(已借出), returned(已歸還)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 借用物品明細表（支援單次借用勾選多項物品）
CREATE TABLE IF NOT EXISTS booking_items (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1
);

-- ==========================================
-- 4. 模組三（志願排課）：課程排課資料表
-- ==========================================
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,           -- 課程名稱
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL, -- 希望/指派的教室
    course_date DATE NOT NULL,                   -- 排課日期（支援週日曆與拖拉修改日期）
    start_time TIME NOT NULL,                    -- 上課開始時間
    end_time TIME NOT NULL,                      -- 上課結束時間
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled', -- wish(老師志願登記), scheduled(已排定)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);