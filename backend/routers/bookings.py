from flask import Blueprint, jsonify
from db import get_conn

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/api/items", methods=["GET"])
def get_items():
    """取得可借用物品清單（鑰匙、投影筆、筆電等）"""
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
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

# TODO (組員 B): 實作週曆借用狀況查詢 (需同時查詢 bookings 與 courses 避免撞期)、新增借用申請、管理員審核與領用/歸還註記