from flask import Blueprint, jsonify
from db import get_conn

spaces_bp = Blueprint("spaces", __name__)


@spaces_bp.route("/api/spaces", methods=["GET"])
def get_spaces():
    """取得所有管院教室資料（模組一公開查詢、模組二/三下拉選單共用）"""
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, room_code, name, floor, capacity, equipment,
                   description, panorama_url, floor_plan_image, map_x, map_y
            FROM rooms
            ORDER BY room_code ASC
            """
        )
        rows = cursor.fetchall()
        rooms = [
            {
                "id": r[0],
                "room_code": r[1],
                "name": r[2],
                "floor": r[3],
                "capacity": r[4],
                "equipment": r[5],
                "description": r[6],
                "panorama_url": r[7],
                "floor_plan_image": r[8],
                "map_x": float(r[9]) if r[9] is not None else None,
                "map_y": float(r[10]) if r[10] is not None else None,
            }
            for r in rows
        ]
        return jsonify({"rooms": rooms}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# TODO (組員 A): 實作 POST /api/spaces (新增教室)、PUT /api/spaces/<id> (修改)、DELETE /api/spaces/<id> (刪除)