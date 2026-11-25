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
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending(待審核), approved(已通過), rejected(已退件)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    room_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) DEFAULT '管理學院',    -- 管理單位
    floor VARCHAR(20),
    capacity INTEGER DEFAULT 0,                  -- 容納人數
    equipment TEXT,                              -- 基本設備說明
    description TEXT,                            -- 教室詳細介紹
    panorama_url TEXT,                           -- 360 全景照片路徑或網址
    floor_plan_image TEXT,                       -- 對應樓層平面圖路徑
    map_x NUMERIC(5, 2),                         -- 教室在平面圖上的 X 座標百分比 (0~100)
    map_y NUMERIC(5, 2),                         -- 教室在平面圖上的 Y 座標百分比 (0~100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 相容舊版資料表：補上 department 欄位並放寬 room_code 長度限制
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS department VARCHAR(100) DEFAULT '管理學院';
ALTER TABLE rooms ALTER COLUMN room_code TYPE VARCHAR(50);

-- 自動清除早期測試資料，避免與正式教室清單重複
DELETE FROM rooms WHERE room_code IN ('管201', '管302', '管405');

-- 寫入管院 25 間真實教室資料
INSERT INTO rooms (room_code, name, department, capacity, equipment, description, map_x, map_y)
VALUES 
    ('管206教室', '管206教室', '國企系', 40, '投影機、手動式布幕', '小型教室', 40.0, 55.0),
    ('管207教室', '管207教室', '國企系', 40, '投影機、手動式布幕', '小型教室', 35.5, 42.0),
    ('管350小型研討室', '管350小型研討室', '國企系', 20, '投影機、移動式白板', '適合專題小組討論與小型會議', 72.0, 38.0),
    ('管432會議室', '管432會議室', '國企系', 20, '投影機、投影布幕、無線網路、有線網路、玻璃白板、冷氣與電扇', '小型會議室', 62.0, 28.5),
    ('管213個案教室', '管213個案教室', '管理學院', 50, '投影幕、布幕、無線麥克風1支、擴大機', '小型教室', 25.0, 60.0),
    ('管215個案教室', '管215個案教室', '管理學院', 100, '投影機、布幕2個、資訊講桌、無線麥克風2支', '大型教室', 48.0, 70.0),
    ('管226巴菲特廳', '管226巴菲特廳', '管理學院', 80, '投影機、布幕、資訊講桌、無線麥克風1支、冷氣', '大型教室', 48.0, 70.0),
    ('管228賈伯斯廳', '管228賈伯斯廳', '管理學院', 100, '投影機、布幕、資訊講桌、無線麥克風1支、冷氣、擴大機', '大型教室', 48.0, 70.0),
    ('管241杜拉克廳', '管241杜拉克廳', '管理學院', 100, '投影機、布幕、資訊講桌、無線麥克風1支、冷氣', '大型教室', 48.0, 70.0),
    ('管260大前研一廳', '管260大前研一廳', '管理學院', 120, '投影機、布幕、資訊講桌、無線麥克風1支、冷氣、白板', '大型教室', 48.0, 70.0),
    ('管268史密斯廳', '管268史密斯廳', '管理學院', 270, '投影機、布幕、影音環控系統、擴大機、無線麥克風9支、白板2個、資訊講桌、冷氣', '大型教室', 48.0, 70.0),
    ('管371寇斯廳', '管371寇斯廳', '管理學院', 250, '投影機、布幕、影音環控系統、擴大機、無線麥克風4支、白板1個、資訊講桌、冷氣', '大型教室', 48.0, 70.0),
    ('管443第二會議室', '管443第二會議室', '管理學院', 60, '投影機、布幕、擴大機、無線麥克風1支、桌上額頸麥克風12座、冷氣', '大型會議室', 48.0, 70.0),
    ('管427第三會議室', '管427第三會議室', '管理學院', 40, '投影機、布幕、冷氣', '小型會議室', 48.0, 70.0),
    ('管B24教室', '管B24教室', '管理學院', 48, '', '小型教室', 48.0, 70.0),
    ('管203教室', '管203教室', '資管系', 40, '投影機、手動式布幕', '小型教室', 48.0, 70.0),
    ('管204教室', '管204教室', '資管系', 40, '投影機、手動式布幕', '小型教室', 48.0, 70.0),
    ('管451小研討室', '管451小研討室', '資管系', 20, '投影機、移動式白板1個', '小型研討室', 48.0, 70.0),
    ('管212教室', '管212教室', '財金系', 40, '投影機、手動式布幕', '小型教室', 48.0, 70.0),
    ('管217小研討室', '管217小研討室', '財金系', 20, '投影機、移動式白板', '小型研討室', 48.0, 70.0),
    ('管210教室', '管210教室', '經濟系', 40, '投影機、手動式布幕', '小型教室', 48.0, 70.0),
    ('管329', '管329', '經濟系', 65, '投影機、布幕', '小型教室', 48.0, 70.0),
    ('管320小研討室', '管320小研討室', '經濟系', 20, '投影機、移動式白板1個', '小型研討室', 48.0, 70.0),
    ('管316小研討室', '管316小研討室', '經濟系', 10, '白板', '小型研討室', 48.0, 70.0),
    ('管331', '管331', '觀光系', 130, '投影機、布幕、電腦', '大型教室', 48.0, 70.0)
ON CONFLICT (room_code) DO UPDATE SET
    name = EXCLUDED.name,
    department = EXCLUDED.department,
    capacity = EXCLUDED.capacity,
    equipment = EXCLUDED.equipment,
    description = EXCLUDED.description,
    map_x = EXCLUDED.map_x,
    map_y = EXCLUDED.map_y;

-- ==========================================
-- 3. 模組二（空間/物品預約借用）：物品、教室可借物品對照表與借用紀錄表
-- ==========================================
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    total_quantity INTEGER NOT NULL DEFAULT 1
);

-- 清除早期測試物品名稱，統一使用正式名稱
DELETE FROM items WHERE name IN ('教室鑰匙', '無線投影筆', 'HDMI轉接頭');

-- 寫入可借用物品與總庫存數量
INSERT INTO items (name, total_quantity)
VALUES 
    ('教室鑰匙（含冷氣遙控器）', 15),
    ('無線簡報投影筆', 6),
    ('借用筆記型電腦', 4),
    ('HDMI / Type-C 轉接頭', 10),
    ('延長線（5公尺）', 6),
    ('白板筆與板擦組', 12)
ON CONFLICT (name) DO UPDATE SET
    total_quantity = EXCLUDED.total_quantity;

-- 教室與可借用物品對照表（設定每間教室分別能借哪些物品）
CREATE TABLE IF NOT EXISTS room_items (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE (room_id, item_id)
);

-- 規則 A：所有教室都能借的通用物品
INSERT INTO room_items (room_id, item_id)
SELECT r.id, i.id FROM rooms r, items i
WHERE i.name IN ('教室鑰匙（含冷氣遙控器）', '白板筆與板擦組')
ON CONFLICT DO NOTHING;

-- 規則 B：指定特定教室才能借的物品（可依實際管理規範自由增減）
INSERT INTO room_items (room_id, item_id)
SELECT r.id, i.id FROM rooms r, items i
WHERE r.name IN ('管206教室', '管207教室', '管432會議室')
  AND i.name IN ('延長線（5公尺）')
ON CONFLICT DO NOTHING;

-- 借用申請主表
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