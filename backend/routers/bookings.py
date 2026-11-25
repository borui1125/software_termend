from datetime import datetime
from flask import Blueprint, jsonify, request
from db import get_conn

bookings_bp = Blueprint("bookings", __name__)


def _parse_time(time_str):
    """將 HH:MM 或 HH:MM:SS 字串轉為 time 物件"""
    fmt = "%H:%M:%S" if len(time_str.strip()) == 8 else "%H:%M"
    return datetime.strptime(time_str.strip(), fmt).time()


@bookings_bp.route("/api/bookings/rooms", methods=["GET"])
def get_booking_rooms():
    """取得可借用教室清單（包含管理單位，使用合併後的教室名稱）"""
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, COALESCE(department, '管理學院'), capacity
            FROM rooms
            ORDER BY name ASC
            """
        )
        rooms = [
            {
                "id": r[0],
                "name": r[1],
                "department": r[2],
                "capacity": r[3],
            }
            for r in cursor.fetchall()
        ]
        return jsonify({"rooms": rooms}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/items", methods=["GET"])
def get_items():
    """取得可借用物品清單（若傳入 room_id，則只回傳該教室可借用的物品）"""
    room_id = request.args.get("room_id", type=int)
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if room_id:
            cursor.execute(
                """
                SELECT i.id, i.name, i.total_quantity
                FROM items i
                JOIN room_items ri ON i.id = ri.item_id
                WHERE ri.room_id = %s
                ORDER BY i.id ASC
                """,
                (room_id,),
            )
        else:
            cursor.execute("SELECT id, name, total_quantity FROM items ORDER BY id ASC")

        items = [{"id": r[0], "name": r[1], "total_quantity": r[2]} for r in cursor.fetchall()]
        return jsonify({"items": items}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings/schedule", methods=["GET"])
def get_room_schedule():
    """查詢指定教室在特定日期區間的佔用時段（整合 courses 排課表 與 bookings 預約表）"""
    room_id = request.args.get("room_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not room_id or not start_date or not end_date:
        return jsonify({"message": "請提供 room_id、start_date 與 end_date"}), 400

    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        events = []

        # 1. 查詢模組三「正式已排定課程」佔用
        cursor.execute(
            """
            SELECT c.id, c.course_name, u.username, c.course_date, c.start_time, c.end_time
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.room_id = %s
              AND c.status = 'scheduled'
              AND c.course_date BETWEEN %s AND %s
            ORDER BY c.course_date ASC, c.start_time ASC
            """,
            (room_id, start_date, end_date),
        )
        for row in cursor.fetchall():
            events.append({
                "source": "course",
                "id": row[0],
                "title": f"[課程] {row[1]}",
                "owner": row[2],
                "date": str(row[3]),
                "start_time": str(row[4])[:5],
                "end_time": str(row[5])[:5],
                "status": "scheduled",
            })

        # 2. 查詢模組二「已通過與審核中預約」佔用
        cursor.execute(
            """
            SELECT b.id, b.purpose, u.username, b.booking_date, b.start_time, b.end_time, b.status
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            WHERE b.room_id = %s
              AND b.status IN ('pending', 'approved')
              AND b.booking_date BETWEEN %s AND %s
            ORDER BY b.booking_date ASC, b.start_time ASC
            """,
            (room_id, start_date, end_date),
        )
        for row in cursor.fetchall():
            events.append({
                "source": "booking",
                "id": row[0],
                "title": row[1] or "教室借用",
                "owner": row[2],
                "date": str(row[3]),
                "start_time": str(row[4])[:5],
                "end_time": str(row[5])[:5],
                "status": row[6],
            })

        events.sort(key=lambda x: (x["date"], x["start_time"]))
        return jsonify({"events": events}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings", methods=["POST"])
def create_booking():
    """送出空間與物品預約申請（含時間重疊衝突檢查與物品庫存檢查）"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    room_id = data.get("room_id")
    booking_date = data.get("booking_date")
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    purpose = (data.get("purpose") or "").strip()
    items = data.get("items") or []

    if not all([user_id, room_id, booking_date, start_time_str, end_time_str, purpose]):
        return jsonify({"message": "請完整填寫教室、日期、起訖時間與借用事由"}), 400

    try:
        t_start = _parse_time(start_time_str)
        t_end = _parse_time(end_time_str)
    except ValueError:
        return jsonify({"message": "時間格式不正確"}), 400

    if t_start >= t_end:
        return jsonify({"message": "結束時間必須晚於開始時間"}), 400

    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # 1. 檢查是否與模組三「已排定課程」衝突
        cursor.execute(
            """
            SELECT course_name, start_time, end_time
            FROM courses
            WHERE room_id = %s
              AND course_date = %s
              AND status = 'scheduled'
              AND start_time < %s
              AND end_time > %s
            """,
            (room_id, booking_date, end_time_str, start_time_str),
        )
        course_conflict = cursor.fetchone()
        if course_conflict:
            return jsonify({
                "message": f"時段衝突：該時段已有正式課程「{course_conflict[0]}」({str(course_conflict[1])[:5]}-{str(course_conflict[2])[:5]})"
            }), 409

        # 2. 檢查是否與模組二「已核准或審核中預約」衝突
        cursor.execute(
            """
            SELECT id, start_time, end_time, status
            FROM bookings
            WHERE room_id = %s
              AND booking_date = %s
              AND status IN ('pending', 'approved')
              AND start_time < %s
              AND end_time > %s
            """,
            (room_id, booking_date, end_time_str, start_time_str),
        )
        booking_conflict = cursor.fetchone()
        if booking_conflict:
            status_zh = "已核准" if booking_conflict[3] == "approved" else "審核中"
            return jsonify({
                "message": f"時段衝突：該教室在 {str(booking_conflict[1])[:5]}-{str(booking_conflict[2])[:5]} 已有「{status_zh}」的預約"
            }), 409

        # 3. 檢查借用物品是否屬於該教室允許借用範圍，且庫存足夠
        for item in items:
            item_id = item.get("item_id")
            req_qty = int(item.get("quantity", 0))
            if req_qty <= 0:
                continue

            cursor.execute(
                """
                SELECT i.name, i.total_quantity
                FROM items i
                JOIN room_items ri ON i.id = ri.item_id
                WHERE i.id = %s AND ri.room_id = %s
                """,
                (item_id, room_id),
            )
            item_row = cursor.fetchone()
            if not item_row:
                return jsonify({"message": "包含該教室未開放借用的物品"}), 400

            item_name, total_qty = item_row[0], item_row[1]

            cursor.execute(
                """
                SELECT COALESCE(SUM(bi.quantity), 0)
                FROM booking_items bi
                JOIN bookings b ON bi.booking_id = b.id
                WHERE bi.item_id = %s
                  AND b.booking_date = %s
                  AND b.status IN ('pending', 'approved')
                  AND b.start_time < %s
                  AND b.end_time > %s
                """,
                (item_id, booking_date, end_time_str, start_time_str),
            )
            used_qty = cursor.fetchone()[0]
            available_qty = total_qty - used_qty

            if req_qty > available_qty:
                return jsonify({
                    "message": f"物品庫存不足：「{item_name}」在該時段僅剩 {max(0, available_qty)} 件可借用"
                }), 409

        # 4. 寫入預約主表與物品明細
        cursor.execute(
            """
            INSERT INTO bookings (user_id, room_id, booking_date, start_time, end_time, purpose, status, handover_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', 'none')
            RETURNING id
            """,
            (user_id, room_id, booking_date, start_time_str, end_time_str, purpose),
        )
        booking_id = cursor.fetchone()[0]

        for item in items:
            item_id = item.get("item_id")
            req_qty = int(item.get("quantity", 0))
            if req_qty > 0:
                cursor.execute(
                    "INSERT INTO booking_items (booking_id, item_id, quantity) VALUES (%s, %s, %s)",
                    (booking_id, item_id, req_qty),
                )

        conn.commit()
        return jsonify({"message": "預約申請已送出，請等待管理員審核", "booking_id": booking_id}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": f"預約建立失敗：{str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings", methods=["GET"])
def list_bookings():
    """查詢借用紀錄（傳入 user_id 查個人紀錄；不傳則回傳全站紀錄供管理員審核）"""
    user_id = request.args.get("user_id", type=int)
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        base_sql = """
            SELECT
                b.id, b.user_id, u.username,
                b.room_id, r.name AS room_name,
                COALESCE(r.department, '管理學院') AS department,
                b.booking_date, b.start_time, b.end_time,
                b.purpose, b.status, b.admin_comment, b.handover_status,
                b.created_at
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN rooms r ON b.room_id = r.id
        """
        if user_id:
            cursor.execute(base_sql + " WHERE b.user_id = %s ORDER BY b.created_at DESC", (user_id,))
        else:
            cursor.execute(base_sql + " ORDER BY b.created_at DESC")

        rows = cursor.fetchall()
        booking_ids = [r[0] for r in rows]

        items_map = {}
        if booking_ids:
            cursor.execute(
                """
                SELECT bi.booking_id, i.name, bi.quantity
                FROM booking_items bi
                JOIN items i ON bi.item_id = i.id
                WHERE bi.booking_id = ANY(%s)
                """,
                (booking_ids,),
            )
            for b_id, i_name, qty in cursor.fetchall():
                items_map.setdefault(b_id, []).append({"name": i_name, "quantity": qty})

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "user_id": r[1],
                "username": r[2],
                "room_id": r[3],
                "room_name": r[4],
                "department": r[5],
                "booking_date": str(r[6]),
                "start_time": str(r[7])[:5],
                "end_time": str(r[8])[:5],
                "purpose": r[9] or "",
                "status": r[10],
                "admin_comment": r[11] or "",
                "handover_status": r[12],
                "created_at": str(r[13]),
                "items": items_map.get(r[0], []),
            })

        return jsonify({"bookings": result}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings/<int:booking_id>/review", methods=["PUT"])
def review_booking(booking_id):
    """管理員審核預約申請（通過 / 退件 + 審核意見）"""
    data = request.get_json() or {}
    new_status = data.get("status")
    admin_comment = (data.get("admin_comment") or "").strip()

    if new_status not in ("approved", "rejected"):
        return jsonify({"message": "無效的審核狀態"}), 400

    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE bookings
            SET status = %s, admin_comment = %s
            WHERE id = %s
            RETURNING id
            """,
            (new_status, admin_comment, booking_id),
        )
        updated = cursor.fetchone()
        if not updated:
            return jsonify({"message": "找不到該筆預約申請"}), 404

        conn.commit()
        return jsonify({"message": "審核狀態已更新"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings/<int:booking_id>/handover", methods=["PUT"])
def update_handover(booking_id):
    """管理員登記鑰匙與物品領用／歸還狀態"""
    data = request.get_json() or {}
    handover_status = data.get("handover_status")

    if handover_status not in ("none", "borrowed", "returned"):
        return jsonify({"message": "無效的領用狀態"}), 400

    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE bookings
            SET handover_status = %s
            WHERE id = %s
            RETURNING id
            """,
            (handover_status, booking_id),
        )
        if not cursor.fetchone():
            return jsonify({"message": "找不到該筆預約申請"}), 404

        conn.commit()
        return jsonify({"message": "領用歸還狀態已更新"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bookings_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    """使用者取消尚未審核的借用申請"""
    user_id = request.args.get("user_id", type=int)
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, status FROM bookings WHERE id = %s", (booking_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"message": "找不到該筆申請"}), 404
        if user_id and row[0] != user_id:
            return jsonify({"message": "無權取消他人的預約申請"}), 403
        if row[1] != "pending":
            return jsonify({"message": "僅可取消「待審核」狀態的申請"}), 400

        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        conn.commit()
        return jsonify({"message": "已取消該筆借用申請"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()